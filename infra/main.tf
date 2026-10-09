terraform {
  required_version = ">= 1.5"

  required_providers {
    neon = {
      source  = "kislerdm/neon"
      version = "0.18.0" # fijada: el repo de este provider está archivado y el oficial saldrá con otro nombre
    }
    render = {
      source  = "render-oss/render"
      version = "1.9.1"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.9.1" # genera el secreto JWT de preprod: así no existe escrito en ningún archivo
    }
  }
}

provider "neon" {}   # lee NEON_API_KEY del entorno
provider "render" {} # lee RENDER_API_KEY y RENDER_OWNER_ID del entorno

# --- El proyecto de Neon de PREPROD: no existe hasta que esto se aplica ---
# Es un proyecto propio (no una base más en el de la app) para poder destruirlo entero
# sin rozar QA ni producción.

resource "neon_project" "preprod" {
  name = "restoflow-preprod"

  # Neon crea los proyectos dentro de una organización y la API exige su id (sin él: "org_id is required").
  # No es un secreto; viene de la variable de entorno TF_VAR_neon_org_id (ver variables.tf).
  org_id = var.neon_org_id

  # Sin esta línea el primer apply falla: el provider pide por defecto 86400 s de historial
  # y el tope del plan gratuito es 21600 (seis horas).
  history_retention_seconds = 21600
}

resource "neon_role" "preprod" {
  project_id = neon_project.preprod.id
  branch_id  = neon_project.preprod.default_branch_id # default_branch_id, NO branch_id
  name       = "app_preprod_owner"
}

resource "neon_database" "preprod" {
  project_id = neon_project.preprod.id
  branch_id  = neon_project.preprod.default_branch_id
  name       = "app_preprod"
  owner_name = neon_role.preprod.name
}

# --- Los dos servicios de PREPROD: corren las imágenes del TP7 (no construyen nada) ---

# Secreto de firma de los tokens: lo genera Terraform, vive en el estado y en el servicio.
resource "random_password" "jwt" {
  length  = 48
  special = false
}

locals {
  # La cadena de conexión se ARMA con lo que devolvió Neon. Nadie la copia y pega:
  # ese era el error más caro del TP6 (un entorno apuntando a la base de otro).
  database_url = "postgresql+psycopg://${neon_role.preprod.name}:${urlencode(neon_role.preprod.password)}@${neon_project.preprod.database_host}/${neon_database.preprod.name}?sslmode=require"
}

resource "render_web_service" "api" {
  name   = "restoflow-api-preprod"
  plan   = "free"
  region = var.region

  runtime_source = {
    image = {
      image_url = var.image_repo_api # SIN la etiqueta pegada
      tag       = var.image_tag      # la etiqueta va en su propio campo
    }
  }

  # No se declara GIT_SHA: viene grabado dentro de la imagen y una variable del servicio lo pisaría.
  env_vars = {
    DATABASE_URL = { value = local.database_url }
    JWT_SECRET   = { value = random_password.jwt.result }
    SERVER_HOST  = { value = "0.0.0.0" }
    SERVER_PORT  = { value = "8080" }
    APP_TIMEZONE = { value = "America/Argentina/Cordoba" }
  }
}

resource "render_web_service" "front" {
  name   = "restoflow-front-preprod"
  plan   = "free"
  region = var.region

  runtime_source = {
    image = {
      image_url = var.image_repo_front
      tag       = var.image_tag
    }
  }

  env_vars = {
    BACKEND_URL  = { value = render_web_service.api.url } # la URL sale de Terraform, no de un copy-paste
    DNS_RESOLVER = { value = "8.8.8.8" }
  }
}
