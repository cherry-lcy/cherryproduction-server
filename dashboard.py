# dashboard.py (fixed)
from flask import Blueprint, render_template, jsonify, request  # Add 'request' here
from extensions import access_logger
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import json
from pathlib import Path

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

class LogAnalyzer:
    """Analyze access logs for visualization"""
    
    def __init__(self, log_dir='logs'):
        self.log_dir = Path(log_dir)
        self.log_file = self.log_dir / 'access.log'
    
    def get_logs_last_days(self, days=7):
        """Get logs from last N days"""
        cutoff = datetime.now() - timedelta(days=days)
        logs = []
        
        if not self.log_file.exists():
            return logs
        
        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    log = json.loads(line.strip())
                    log_time = datetime.fromisoformat(log['timestamp'])
                    if log_time >= cutoff:
                        logs.append(log)
                except:
                    continue
        
        return logs
    
    def get_hourly_traffic(self, days=7):
        """Get traffic distribution by hour"""
        logs = self.get_logs_last_days(days)
        hourly = defaultdict(int)
        
        for log in logs:
            hour = datetime.fromisoformat(log['timestamp']).hour
            hourly[hour] += 1
        
        return [{'hour': h, 'count': hourly[h]} for h in range(24)]
    
    def get_daily_traffic(self, days=7):
        """Get daily traffic trends"""
        logs = self.get_logs_last_days(days)
        daily = defaultdict(int)
        
        for log in logs:
            date = datetime.fromisoformat(log['timestamp']).date()
            daily[date.isoformat()] += 1
        
        return [{'date': d, 'count': daily[d]} for d in sorted(daily.keys())]
    
    def get_status_code_distribution(self, days=7):
        """Get HTTP status code distribution"""
        logs = self.get_logs_last_days(days)
        status_counts = Counter(log['status_code'] for log in logs)
        
        return [{'status': str(k), 'count': v} for k, v in status_counts.items()]
    
    def get_popular_paths(self, limit=10, days=7):
        """Get most visited paths"""
        logs = self.get_logs_last_days(days)
        path_counts = Counter(log['path'] for log in logs)
        
        return [{'path': path, 'count': count} 
                for path, count in path_counts.most_common(limit)]
    
    def get_response_time_stats(self, days=7):
        """Get response time statistics"""
        logs = self.get_logs_last_days(days)
        durations = [log['duration_ms'] for log in logs if log['duration_ms'] > 0]
        
        if not durations:
            return {'avg': 0, 'max': 0, 'min': 0, 'p95': 0}
        
        durations.sort()
        p95_idx = int(len(durations) * 0.95)
        
        return {
            'avg': round(sum(durations) / len(durations), 2),
            'max': max(durations),
            'min': min(durations),
            'p95': durations[p95_idx] if p95_idx < len(durations) else durations[-1]
        }
    
    def get_top_user_agents(self, limit=5, days=7):
        """Get most common user agents"""
        logs = self.get_logs_last_days(days)
        ua_counts = Counter()
        
        for log in logs:
            ua = log.get('user_agent', 'Unknown')[:50]
            if 'Chrome' in ua:
                ua_counts['Chrome'] += 1
            elif 'Firefox' in ua:
                ua_counts['Firefox'] += 1
            elif 'Safari' in ua and 'Chrome' not in ua:
                ua_counts['Safari'] += 1
            elif 'Edge' in ua:
                ua_counts['Edge'] += 1
            elif 'Postman' in ua or 'curl' in ua:
                ua_counts['API Client'] += 1
            else:
                ua_counts['Other'] += 1
        
        return [{'browser': browser, 'count': count} 
                for browser, count in ua_counts.most_common(limit)]
    
    def get_total_stats(self, days=7):
        """Get overall statistics"""
        logs = self.get_logs_last_days(days)
        
        if not logs:
            return {
                'total_requests': 0,
                'unique_ips': 0,
                'avg_response_time': 0,
                'error_rate': 0,
                'success_rate': 0
            }
        
        total = len(logs)
        errors = sum(1 for log in logs if log['status_code'] >= 400)
        unique_ips = len(set(log['ip'] for log in logs if log['ip']))
        
        return {
            'total_requests': total,
            'unique_ips': unique_ips,
            'avg_response_time': round(sum(l['duration_ms'] for l in logs) / total, 2),
            'error_rate': round((errors / total) * 100, 2),
            'success_rate': round(((total - errors) / total) * 100, 2)
        }


analyzer = LogAnalyzer()

@dashboard_bp.route('/')
def dashboard():
    """Render the dashboard page"""
    return render_template('dashboard.html')

@dashboard_bp.route('/api/stats')
def get_stats():
    """API endpoint for dashboard data"""
    days = request.args.get('days', 7, type=int)
    
    return jsonify({
        'total_stats': analyzer.get_total_stats(days),
        'hourly_traffic': analyzer.get_hourly_traffic(days),
        'daily_traffic': analyzer.get_daily_traffic(days),
        'status_codes': analyzer.get_status_code_distribution(days),
        'popular_paths': analyzer.get_popular_paths(10, days),
        'response_times': analyzer.get_response_time_stats(days),
        'user_agents': analyzer.get_top_user_agents(5, days)
    })