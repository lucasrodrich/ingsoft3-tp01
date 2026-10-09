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
  }
}

provider "neon" {}   # lee NEON_API_KEY del entorno
provider "render" {} # lee RENDER_API_KEY y RENDER_OWNER_ID del entorno

# --- El proyecto de Neon de PREPROD: no existe hasta que esto se aplica ---
# Es un proyecto propio (no una base más en el de la app) para poder destruirlo entero
# sin rozar QA ni producción.

resource "neon_project" "preprod" {
  name = "restoflow-preprod"

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
