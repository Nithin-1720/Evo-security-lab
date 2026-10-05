# ============================================================
# EVO VULNERABLE AI LAB
#
# INTENTIONALLY INSECURE TERRAFORM.
# DO NOT APPLY THIS CONFIGURATION.
# SCANNING LAB ONLY.
# ============================================================


terraform {
  required_providers {

    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }

  }
}


provider "aws" {

  region = "us-east-1"

}


# ------------------------------------------------------------
# LAB-IAC-001
#
# Security group open to the entire Internet.
# ------------------------------------------------------------

resource "aws_security_group" "open_everything" {

  name = "evo-lab-open-everything"


  ingress {

    description = "INTENTIONALLY OPEN"

    from_port = 0
    to_port   = 0

    protocol = "-1"

    cidr_blocks = [
      "0.0.0.0/0"
    ]

  }


  egress {

    from_port = 0
    to_port   = 0

    protocol = "-1"

    cidr_blocks = [
      "0.0.0.0/0"
    ]

  }

}


# ------------------------------------------------------------
# LAB-IAC-002
#
# Public S3 bucket.
# ------------------------------------------------------------

resource "aws_s3_bucket" "public_data" {

  bucket = "evo-vulnerable-ai-lab-demo-bucket"

  force_destroy = true

}


resource "aws_s3_bucket_public_access_block" "public_data" {

  bucket = aws_s3_bucket.public_data.id


  block_public_acls = false

  block_public_policy = false

  ignore_public_acls = false

  restrict_public_buckets = false

}


resource "aws_s3_bucket_acl" "public_data" {

  bucket = aws_s3_bucket.public_data.id

  acl = "public-read"

}


# ------------------------------------------------------------
# LAB-IAC-003
#
# Public and unencrypted database.
# ------------------------------------------------------------

resource "aws_db_instance" "lab_database" {

  identifier = "evo-vulnerable-ai-lab-db"


  allocated_storage = 20


  engine = "mysql"


  instance_class = "db.t3.micro"


  username = "admin"


  #
  # INTENTIONALLY HARDCODED LAB PASSWORD.
  #

  password = "LabDatabasePassword123!"


  publicly_accessible = true


  storage_encrypted = false


  backup_retention_period = 0


  skip_final_snapshot = true


  deletion_protection = false

}


# ------------------------------------------------------------
# LAB-IAC-004
#
# Public EC2 instance with weak metadata protection.
# ------------------------------------------------------------

resource "aws_instance" "lab_server" {

  ami = "ami-1234567890abcdef0"


  instance_type = "t3.micro"


  associate_public_ip_address = true


  vpc_security_group_ids = [

    aws_security_group.open_everything.id

  ]


  metadata_options {

    http_endpoint = "enabled"

    #
    # Allows IMDSv1.
    #

    http_tokens = "optional"

  }


  user_data = <<-EOF

    #!/bin/bash

    export INTERNAL_API_KEY="EVO-LAB-INTERNAL-KEY"

    echo "debug=true" > /tmp/app.conf

  EOF

}


# ------------------------------------------------------------
# LAB-IAC-005
#
# Administrator-equivalent IAM policy.
# ------------------------------------------------------------

resource "aws_iam_policy" "everything_admin" {

  name = "evo-lab-everything-admin"


  policy = jsonencode({

    Version = "2012-10-17"


    Statement = [

      {

        Effect = "Allow"


        Action = [

          "*"

        ]


        Resource = [

          "*"

        ]

      }

    ]

  })

}