terraform {
  backend "s3" {
    encrypt      = true
    key          = "ownership-scanner/dev/terraform.tfstate"
    use_lockfile = true
  }
}
