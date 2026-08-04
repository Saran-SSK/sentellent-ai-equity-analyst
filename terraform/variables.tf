variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Project Name"
  type        = string
  default     = "sentellent-ai"
}

variable "vpc_cidr" {
  description = "VPC CIDR Block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "Public Subnet CIDR Blocks"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "availability_zones" {
  description = "Availability Zones"
  type        = list(string)
  default     = ["ap-south-1a", "ap-south-1b"]
}

variable "db_username" {
  description = "Database Username"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Database Password"
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "Database Name"
  type        = string
  default     = "sentellent"
}

variable "jwt_secret" {
  description = "JWT Secret for authentication"
  type        = string
  sensitive   = true
}

variable "google_client_id" {
  description = "Google OAuth Client ID"
  type        = string
  sensitive   = true
}

variable "google_client_secret" {
  description = "Google OAuth Client Secret"
  type        = string
  sensitive   = true
}

variable "gemini_api_key" {
  description = "Gemini API Key for AI features"
  type        = string
  sensitive   = true
}

variable "frontend_container_port" {
  description = "Frontend Container Port"
  type        = number
  default     = 3000
}

variable "backend_container_port" {
  description = "Backend Container Port"
  type        = number
  default     = 8000
}

variable "frontend_cpu" {
  description = "Frontend Task CPU"
  type        = number
  default     = 256
}

variable "frontend_memory" {
  description = "Frontend Task Memory"
  type        = number
  default     = 512
}

variable "backend_cpu" {
  description = "Backend Task CPU"
  type        = number
  default     = 256
}

variable "backend_memory" {
  description = "Backend Task Memory"
  type        = number
  default     = 512
}

variable "db_instance_class" {
  description = "RDS Instance Class"
  type        = string
  default     = "db.t3.micro"
}

variable "finnhub_api_key" {
  description = "Finnhub API Key"
  type        = string
  sensitive   = true
}

variable "alpha_vantage_api_key" {
  description = "Alpha Vantage API Key"
  type        = string
  sensitive   = true
}

variable "qdrant_url" {
  type = string
}

variable "qdrant_api_key" {
  type      = string
  sensitive = true
}

variable "nextauth_secret" {
  description = "NextAuth secret"
  type        = string
  sensitive   = true
}