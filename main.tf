provider "aws" {
  region = "us-east-1"
}

# ---------------------------------------------------------
# VULNERABILITY 1: Unencrypted, Publicly Accessible S3 Bucket
# ---------------------------------------------------------
resource "aws_s3_bucket" "insecure_bucket" {
  bucket = "company-public-data-bucket-123"
}

resource "aws_s3_bucket_public_access_block" "insecure_bucket_access" {
  bucket = aws_s3_bucket.insecure_bucket.id

  # DANGEROUS: Explicitly disabling public access blocks
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# ---------------------------------------------------------
# VULNERABILITY 2: Security Group Wide Open to the Internet
# ---------------------------------------------------------
resource "aws_security_group" "web_sg" {
  name        = "allow_all_traffic"
  description = "Allow all inbound traffic"

  ingress {
    description = "SSH from anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    # DANGEROUS: Allowing SSH access from 0.0.0.0/0
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP from anywhere"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ---------------------------------------------------------
# VULNERABILITY 3: EC2 Instance Misconfigurations
# ---------------------------------------------------------
resource "aws_instance" "web_server" {
  ami                         = "ami-0c55b159cbfafe1f0"
  instance_type               = "t2.micro"
  # DANGEROUS: Automatically assigning a public IP
  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.web_sg.id]

  # DANGEROUS: Hardcoding secrets into the EC2 User Data script
  user_data = <<-EOF
              #!/bin/bash
              echo "export DB_PASSWORD=super_secret_db_pass" >> /etc/environment
              EOF
}
