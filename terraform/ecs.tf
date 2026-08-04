# ECS Configuration
# Elastic Container Service with Fargate for container orchestration

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name        = "${var.project_name}-cluster"
    Environment = "production"
  }
}

# CloudWatch Log Group for ECS
resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/${var.project_name}"
  retention_in_days = 7

  tags = {
    Name        = "${var.project_name}-ecs-logs"
    Environment = "production"
  }
}

# Frontend Task Definition (Next.js)
resource "aws_ecs_task_definition" "frontend" {
  family                   = "${var.project_name}-frontend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.frontend_cpu
  memory                   = var.frontend_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "frontend"
      image     = "${aws_ecr_repository.frontend.repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = var.frontend_container_port
          protocol      = "tcp"
        }
      ]
      environment = [
  {
    name  = "NEXT_PUBLIC_API_URL"
    value = "http://${aws_lb.main.dns_name}"
  },
  {
    name  = "GOOGLE_CLIENT_ID"
    value = var.google_client_id
  },
  {
    name  = "GOOGLE_CLIENT_SECRET"
    value = var.google_client_secret
  },
  {
    name  = "NEXTAUTH_SECRET"
    value = var.nextauth_secret
  },
  {
    name  = "NEXTAUTH_URL"
    value = "http://${aws_lb.main.dns_name}"
  },
  {
    name  = "AUTH_TRUST_HOST"
    value = "true"
  },
  {
  name  = "DEPLOYMENT_VERSION"
  value = "frontend-v5"
  }
]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "frontend"
        }
      }
    }        
  ])

  tags = {
    Name        = "${var.project_name}-frontend-td"
    Environment = "production"
  }
}

# Backend Task Definition (FastAPI)
resource "aws_ecs_task_definition" "backend" {
  family                   = "${var.project_name}-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.backend_cpu
  memory                   = var.backend_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "backend"
      image     = "${aws_ecr_repository.backend.repository_url}:latest"
      essential = true
      portMappings = [
        {
          containerPort = var.backend_container_port
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "DATABASE_URL"
          value = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.main.endpoint}/${var.db_name}"
        },
        {
          name  = "JWT_SECRET"
          value = var.jwt_secret
        },
        {
        name  = "GOOGLE_CLIENT_ID"
        value = var.google_client_id
        },
        {
        name  = "GOOGLE_CLIENT_SECRET"
        value = var.google_client_secret
        },
        {
          name  = "GOOGLE_OAUTH_CLIENT_ID"
          value = var.google_client_id
        },
        {
          name  = "GOOGLE_OAUTH_CLIENT_SECRET"
          value = var.google_client_secret
        },
        {
          name  = "GEMINI_API_KEY"
          value = var.gemini_api_key
        },
        {
        name  = "FINNHUB_API_KEY"
        value = var.finnhub_api_key
        },
        {
        name  = "ALPHA_VANTAGE_API_KEY"
        value = var.alpha_vantage_api_key
        },
        {
        name  = "QDRANT_URL"
        value = var.qdrant_url
        },
        {
        name  = "QDRANT_API_KEY"
        value = var.qdrant_api_key
        }
      ]
      secrets = []
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "backend"
        }
      }
    }
  ])

  tags = {
    Name        = "${var.project_name}-backend-td"
    Environment = "production"
  }
}

# Frontend ECS Service
resource "aws_ecs_service" "frontend" {
  name            = "${var.project_name}-frontend-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.frontend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.public[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.frontend.arn
    container_name   = "frontend"
    container_port   = var.frontend_container_port
  }

  depends_on = [aws_lb_listener.http]

  tags = {
    Name        = "${var.project_name}-frontend-service"
    Environment = "production"
  }
}

# Backend ECS Service
resource "aws_ecs_service" "backend" {
  name            = "${var.project_name}-backend-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.public[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend"
    container_port   = var.backend_container_port
  }

  depends_on = [aws_lb_listener.http]

  tags = {
    Name        = "${var.project_name}-backend-service"
    Environment = "production"
  }
}
