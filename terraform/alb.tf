# ALB Configuration
# Application Load Balancer for distributing traffic to ECS services
# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
  enable_deletion_protection = false
  tags = {
    Name        = "${var.project_name}-alb"
    Environment = "production"
  }
}
# Target Group for Frontend
resource "aws_lb_target_group" "frontend" {
  name        = "${var.project_name}-frontend-tg"
  port        = var.frontend_container_port
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"
  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 30
    matcher             = "200"
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
  }
  tags = {
    Name        = "${var.project_name}-frontend-tg"
    Environment = "production"
  }
}
# Target Group for Backend
resource "aws_lb_target_group" "backend" {
  name        = "${var.project_name}-backend-tg"
  port        = var.backend_container_port
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"
  deregistration_delay = 300
  health_check {
  enabled             = true
  healthy_threshold   = 2
  unhealthy_threshold = 3
  interval            = 30
  timeout             = 5
  matcher             = "200"
  path                = "/api/v1/health"
  port                = "traffic-port"
  protocol            = "HTTP"
}
  tags = {
    Name        = "${var.project_name}-backend-tg"
    Environment = "production"
  }
}
# HTTP Listener - Routes to target groups based on path
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend.arn
  }
}
# Listener Rule to route /api/v1/* to backend (but NOT /api/auth/*)
resource "aws_lb_listener_rule" "backend_api" {
  listener_arn = aws_lb_listener.http.arn
  priority     = 100
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }
  condition {
    path_pattern {
      values = ["/api/v1/*"]
    }
  }
}
