# Production Debugging & Monitoring Setup Guide

This guide provides comprehensive setup instructions for the warehouse settings production debugging and monitoring system.

## 🎯 Overview

The debugging system provides:

- **Real-time error monitoring** with automatic classification
- **Performance monitoring** with alerts and thresholds  
- **Database migration debugging** with constraint validation
- **API layer debugging** with request tracing
- **Frontend state management debugging** with infinite loop detection
- **Automated testing framework** for regression detection
- **Deployment health checking** with rollback triggers

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend

# Install monitoring dependencies
pip install psutil requests

# Set environment variables
export MONITORING_ENABLED=true
export DEBUG_MONITORING=false  # Set to true for verbose logging
export PERFORMANCE_TRACKING=true
export HEALTH_CHECK_INTERVAL=30  # seconds
export AUTO_ROLLBACK_ENABLED=false  # Set to true for production
```

### 2. Frontend Setup

```bash
cd frontend

# Enable debug tools in development
localStorage.setItem('debug-enabled', 'true')

# Access the comprehensive debug dashboard
http://localhost:3000/debug-comprehensive
```

### 3. Environment Configuration

Create `.env` file in backend:

```bash
# Monitoring Configuration
MONITORING_ENABLED=true
DEBUG_MONITORING=false
PERFORMANCE_TRACKING=true
HEALTH_CHECK_INTERVAL=30
AUTO_ROLLBACK_ENABLED=false

# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database

# API Configuration
API_BASE_URL=http://localhost:5000
FRONTEND_URL=http://localhost:3000

# Alert Configuration (optional)
ROLLBACK_WEBHOOK_URL=https://your-deployment-system/webhook/rollback
SLACK_WEBHOOK_URL=https://hooks.slack.com/your-webhook

# File Upload Limits
UPLOAD_MAX_SIZE=10485760  # 10MB
```

## 📊 Monitoring Endpoints

### Backend API Endpoints

```bash
# System Health
GET /api/v1/monitoring/health
GET /api/v1/monitoring/errors?hours=24
GET /api/v1/monitoring/performance?hours=24
GET /api/v1/monitoring/database?hours=24

# Migration Debugging
GET /api/v1/debug/schema-validation
GET /api/v1/debug/migration-report
GET /api/v1/debug/migration-health

# API Debugging
GET /api/v1/debug/api-stats
GET /api/v1/debug/warehouse-health
GET /api/v1/debug/request/<request_id>

# Test Framework
POST /api/v1/debug/run-tests
GET /api/v1/debug/test-status

# Deployment Health
GET /api/v1/deployment/health
POST /api/v1/deployment/start-monitoring
POST /api/v1/deployment/stop-monitoring

# Comprehensive Dashboard
GET /api/v1/debug/dashboard
```

### Frontend Debug Pages

```bash
# Comprehensive Debug Dashboard
/debug-comprehensive

# Performance Monitoring
/debug-comprehensive?tab=performance

# State Management Debugging
/debug-comprehensive?tab=state

# Migration Status
/debug-comprehensive?tab=migration

# Test Results
/debug-comprehensive?tab=tests
```

## 🔧 Configuration Options

### 1. Monitoring Configuration

```python
# Backend monitoring settings
_monitoring_state = {
    'enabled': True,
    'debug_mode': False,  # Verbose logging
    'performance_tracking': True
}

# Performance thresholds
slow_endpoint_threshold = 2000  # ms
memory_alert_threshold = 500   # MB
error_rate_threshold = 0.05    # 5%
```

### 2. Health Check Configuration

```python
# Health check settings
check_interval = 30  # seconds
rollback_enabled = False
frontend_url = 'http://localhost:3000'
api_base_url = 'http://localhost:5000'

# Rollback triggers
rollback_triggers = [
    ('high_error_rate', 0.1),        # 10% error rate
    ('database_failures', 3),        # 3 consecutive failures
    ('slow_response_times', 5000),   # 5 seconds
    ('memory_exhaustion', 95),       # 95% memory usage
    ('warehouse_failures', 0.5)      # 50% failure rate
]
```

### 3. Frontend Debug Configuration

```typescript
// Frontend debug settings
const debugConfig = {
  enabled: process.env.NODE_ENV === 'development',
  autoRefresh: true,
  refreshInterval: 5000,  // ms
  maxStateChanges: 500,
  maxRenderLogs: 1000,
  maxEffectTraces: 500
}
```

## 🚨 Alert Configuration

### 1. Error Monitoring Alerts

- **Critical errors**: Immediate notification
- **High error rates**: Alert if >5% of requests fail
- **Database failures**: Alert on connection issues
- **Performance degradation**: Alert if response times >2x baseline

### 2. Performance Alerts

- **Slow endpoints**: Alert if avg response time >2s
- **High memory usage**: Alert if memory >85%
- **Database slow queries**: Alert if queries >500ms
- **Frontend infinite loops**: Immediate alert

### 3. Deployment Health Alerts

- **Schema validation failures**: Block deployment
- **Health check failures**: Trigger rollback consideration
- **Test failures**: Alert and investigate
- **System resource exhaustion**: Emergency alert

## 🎛️ Dashboard Usage

### 1. Overview Tab

- **System Health**: Overall status with key metrics
- **Resource Usage**: CPU, memory, disk usage
- **Recent Errors**: Latest system errors
- **Health Checks**: All system health check results

### 2. Performance Tab

- **Response Times**: API endpoint performance
- **Database Performance**: Query times and slow queries
- **System Metrics**: Historical CPU/memory usage
- **Error Rates**: Error trends over time

### 3. State Debug Tab

- **Component Renders**: React re-render tracking
- **useEffect Traces**: Effect execution monitoring
- **State Changes**: Zustand store modifications
- **Performance Issues**: Infinite loops and slow renders

### 4. Migration Tab

- **Schema Validation**: Database schema health
- **Migration Status**: Current migration state
- **Constraint Issues**: Foreign key and constraint problems
- **Table Statistics**: Database table activity

### 5. Tests Tab

- **Test Results**: Automated test execution
- **Test Coverage**: Available test suites
- **Regression Detection**: Comparison with baselines
- **Performance Tests**: Load testing results

## 🚀 Deployment Process

### Pre-Deployment

1. **Establish Baseline**:
   ```bash
   # Start pre-deployment monitoring
   curl -X POST http://localhost:5000/api/v1/deployment/start-monitoring \
     -H "Content-Type: application/json" \
     -d '{"phase": "pre_deployment"}'
   ```

2. **Run Full Test Suite**:
   ```bash
   # Execute all tests
   curl -X POST http://localhost:5000/api/v1/debug/run-tests \
     -H "Content-Type: application/json" \
     -d '{"parallel": true}'
   ```

3. **Validate Schema**:
   ```bash
   # Check database schema
   curl http://localhost:5000/api/v1/debug/schema-validation
   ```

### During Deployment

1. **Switch to Deployment Monitoring**:
   ```bash
   curl -X POST http://localhost:5000/api/v1/deployment/start-monitoring \
     -H "Content-Type: application/json" \
     -d '{"phase": "deployment"}'
   ```

2. **Monitor Health Continuously**:
   ```bash
   # Check deployment health every 30 seconds
   while true; do
     curl http://localhost:5000/api/v1/deployment/health
     sleep 30
   done
   ```

### Post-Deployment

1. **Switch to Post-Deployment Monitoring**:
   ```bash
   curl -X POST http://localhost:5000/api/v1/deployment/start-monitoring \
     -H "Content-Type: application/json" \
     -d '{"phase": "post_deployment"}'
   ```

2. **Run Regression Tests**:
   ```bash
   curl -X POST http://localhost:5000/api/v1/debug/run-tests \
     -H "Content-Type: application/json" \
     -d '{"parallel": true}'
   ```

3. **Monitor for 24 Hours**: Keep monitoring active for first 24 hours

## 🔍 Troubleshooting Guide

### Common Issues

1. **High Error Rates**:
   - Check `/api/v1/monitoring/errors` for error details
   - Look for database constraint violations
   - Verify API endpoint responses

2. **Slow Performance**:
   - Check `/api/v1/monitoring/performance` for metrics
   - Identify slow database queries
   - Review API response times

3. **Database Issues**:
   - Run `/api/v1/debug/schema-validation`
   - Check migration health with `/api/v1/debug/migration-health`
   - Review constraint violations

4. **Frontend State Issues**:
   - Access `/debug-comprehensive?tab=state`
   - Check for infinite useEffect loops
   - Review component re-render patterns

5. **Test Failures**:
   - Check `/api/v1/debug/test-status`
   - Run tests individually for detailed results
   - Review test environment setup

### Debug Commands

```bash
# Backend debugging
curl http://localhost:5000/api/v1/debug/dashboard

# Frontend debugging (in browser console)
debugFrontend.enable()
debugFrontend.report(60000)  # Last 60 seconds
debugFrontend.getStateChanges()
debugFrontend.clear()

# Database debugging
curl http://localhost:5000/api/v1/debug/migration-report

# Performance debugging
curl http://localhost:5000/api/v1/monitoring/performance?hours=1
```

## 📋 Production Checklist

### Before Deployment
- [ ] All tests passing
- [ ] Schema validation clean
- [ ] Performance baselines established
- [ ] Rollback procedures tested
- [ ] Monitoring system active

### During Deployment
- [ ] Health monitoring enabled
- [ ] Error rates within thresholds
- [ ] Response times acceptable
- [ ] Database operations successful
- [ ] No rollback triggers activated

### After Deployment
- [ ] Post-deployment tests passed
- [ ] User acceptance testing complete
- [ ] Performance within 10% of baseline
- [ ] Error rates <1%
- [ ] All critical paths functional

### 24-Hour Monitoring
- [ ] System stability confirmed
- [ ] No critical errors
- [ ] Performance degradation <5%
- [ ] User reports normal
- [ ] Ready for normal monitoring

## 🛠️ Advanced Configuration

### Custom Rollback Triggers

```python
# Add custom rollback trigger
custom_trigger = RollbackTrigger(
    name="custom_business_metric",
    condition="business_metric > threshold",
    threshold=1000,
    triggered=False
)
deployment_health_checker.rollback_triggers.append(custom_trigger)
```

### Custom Health Checks

```python
# Add custom health check
def check_business_logic():
    # Your custom health check logic
    return HealthCheckResult(
        check_name="business_logic",
        status=HealthStatus.HEALTHY,
        message="Business logic working correctly"
    )

deployment_health_checker.health_checks.append(check_business_logic)
```

### Webhook Integration

```bash
# Configure rollback webhook
export ROLLBACK_WEBHOOK_URL="https://your-ci-cd.com/rollback"

# Configure Slack alerts
export SLACK_WEBHOOK_URL="https://hooks.slack.com/your-webhook"
```

This comprehensive debugging and monitoring system ensures production stability and provides immediate insight into any issues during deployment or normal operations.

## 🔧 Key Benefits

1. **Proactive Issue Detection**: Catch problems before users do
2. **Rapid Debugging**: Pinpoint issues quickly with detailed context
3. **Automated Recovery**: Rollback triggers prevent prolonged outages
4. **Performance Insights**: Optimize based on real usage data
5. **Deployment Confidence**: Validate changes automatically
6. **Historical Analysis**: Track trends and patterns over time

The system is designed to be production-ready with minimal performance impact while providing maximum visibility into system health and performance.