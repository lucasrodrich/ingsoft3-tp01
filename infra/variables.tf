variable "neon_org_id" {
  type        = string
  description = "Id de la organización de Neon (consola de Neon -> Organization settings). Se pasa con TF_VAR_neon_org_id."
}

# Estos valores NO son secretos (una imagen pública, una etiqueta, una región): van con default y se commitean.
variable "image_repo_api" {
  type    = string
  default = "ghcr.io/lucasrodrich/ingsoft3-tp01-backend" # SIN la etiqueta
}

variable "image_repo_front" {
  type    = string
  default = "ghcr.io/lucasrodrich/ingsoft3-tp01-frontend" # SIN la etiqueta
}

variable "image_tag" {
  type        = string
  description = "Etiqueta sha-<40 caracteres> de un merge del TP7. Preprod corre la imagen de ese commit."
  default     = "sha-5233d0bc8d63f6079e1272f84be170c081daee44" # el commit de v7.0.0
}

variable "region" {
  type    = string
  default = "oregon" # frankfurt | ohio | oregon | singapore | virginia
}
