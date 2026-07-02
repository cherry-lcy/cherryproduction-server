# dashboard.py
from flask import Blueprint, render_template, jsonify, request
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
    
    def _parse_timestamp(self, timestamp_str):
        """Parse timestamp string safely"""
        if not timestamp_str:
            return None
        try:
            if timestamp_str.endswith('Z'):
                timestamp_str = timestamp_str[:-1]
            try:
                return datetime.fromisoformat(timestamp_str)
            except ValueError:
                if '.' in timestamp_str:
                    dt_part = timestamp_str.split('.')[0]
                    return datetime.fromisoformat(dt_part)
                else:
                    return datetime.fromisoformat(timestamp_str)
        except (ValueError, TypeError):
            return None
    
    def get_logs_last_days(self, days=7):
        """Get logs from last N days"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        logs = []
        
        if not self.log_file.exists():
            return logs
        
        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    log = json.loads(line.strip())
                    timestamp_str = log.get('timestamp', '')
                    if not timestamp_str:
                        continue
                    log_time = self._parse_timestamp(timestamp_str)
                    if log_time is None:
                        continue
                    if log_time >= cutoff:
                        logs.append(log)
                except (json.JSONDecodeError, ValueError):
                    continue
        return logs
    
    def get_hourly_traffic(self, days=7):
        """Get traffic distribution by hour"""
        logs = self.get_logs_last_days(days)
        hourly = defaultdict(int)
        for log in logs:
            log_time = self._parse_timestamp(log.get('timestamp', ''))
            if log_time is not None:
                hourly[log_time.hour] += 1
        return [{'hour': h, 'count': hourly[h]} for h in range(24)]
    
    def get_daily_traffic(self, days=7):
        """Get daily traffic trends for the LAST N days (including today)"""
        logs = self.get_logs_last_days(days)
        daily = defaultdict(int)
        
        for log in logs:
            log_time = self._parse_timestamp(log.get('timestamp', ''))
            if log_time is not None:
                date = log_time.date()
                daily[date.isoformat()] += 1
        
        # Generate ALL dates in the range (including days with 0 visits)
        result = []
        today = datetime.utcnow().date()
        for i in range(days - 1, -1, -1):  # Go from oldest to newest
            date = today - timedelta(days=i)
            date_str = date.isoformat()
            result.append({'date': date_str, 'count': daily.get(date_str, 0)})
        
        return result
    
    def get_cumulative_traffic(self, days=7):
        """Get cumulative traffic over time (running total)"""
        daily_data = self.get_daily_traffic(days)
        cumulative = 0
        result = []
        for item in daily_data:
            cumulative += item['count']
            result.append({
                'date': item['date'],
                'cumulative': cumulative
            })
        return result
    
    def get_status_code_distribution(self, days=7):
        """Get HTTP status code distribution"""
        logs = self.get_logs_last_days(days)
        status_counts = Counter()
        for log in logs:
            status = log.get('status_code') or log.get('httpStatus')
            if status is not None:
                try:
                    status_counts[int(status)] += 1
                except (ValueError, TypeError):
                    continue
        return [{'status': str(k), 'count': v} for k, v in sorted(status_counts.items())]
    
    def get_popular_paths(self, limit=10, days=7):
        """Get most visited paths"""
        logs = self.get_logs_last_days(days)
        path_counts = Counter()
        
        # Skip these paths (they clutter the data)
        SKIP_PATHS = {'/', '/health', '/courses', '/dashboard', '/dashboard/api/stats'}
        
        for log in logs:
            path = log.get('path', '')
            if path and path not in SKIP_PATHS:
                # Clean up path
                if path != '/':
                    path = path.rstrip('/')
                path_counts[path] += 1
        
        return [{'path': path, 'count': count} 
                for path, count in path_counts.most_common(limit)]
    
    def get_response_time_stats(self, days=7):
        """Get response time statistics"""
        logs = self.get_logs_last_days(days)
        durations = []
        for log in logs:
            duration = log.get('duration_ms') or log.get('durationMs')
            if duration is not None:
                try:
                    duration = float(duration)
                    if duration > 0:
                        durations.append(duration)
                except (ValueError, TypeError):
                    continue
        
        if not durations:
            return {'avg': 0, 'max': 0, 'min': 0, 'p95': 0}
        
        durations.sort()
        p95_idx = min(int(len(durations) * 0.95), len(durations) - 1)
        
        return {
            'avg': round(sum(durations) / len(durations), 2),
            'max': max(durations),
            'min': min(durations),
            'p95': durations[p95_idx] if durations else 0
        }
    
    def get_top_user_agents(self, limit=5, days=7):
        """Get most common user agents"""
        logs = self.get_logs_last_days(days)
        ua_counts = defaultdict(int)
        
        for log in logs:
            ua = log.get('user_agent', '')
            if not ua:
                continue
            
            ua_lower = ua.lower()
            if 'chrome' in ua_lower and 'edg' not in ua_lower and 'opr' not in ua_lower:
                ua_counts['Chrome'] += 1
            elif 'firefox' in ua_lower:
                ua_counts['Firefox'] += 1
            elif 'safari' in ua_lower and 'chrome' not in ua_lower:
                ua_counts['Safari'] += 1
            elif 'edg' in ua_lower:
                ua_counts['Edge'] += 1
            elif 'opr' in ua_lower or 'opera' in ua_lower:
                ua_counts['Opera'] += 1
            elif 'bot' in ua_lower or 'crawler' in ua_lower or 'spider' in ua_lower:
                ua_counts['Bot/Crawler'] += 1
            elif 'postman' in ua_lower or 'curl' in ua_lower or 'python' in ua_lower:
                ua_counts['API Client'] += 1
            else:
                ua_counts['Other'] += 1
        
        sorted_items = sorted(ua_counts.items(), key=lambda x: x[1], reverse=True)
        return [{'browser': browser, 'count': count} 
                for browser, count in sorted_items[:limit]]
    
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
        errors = 0
        total_duration = 0
        ips = set()
        
        for log in logs:
            status = log.get('status_code') or log.get('httpStatus')
            if status is not None:
                try:
                    if int(status) >= 400:
                        errors += 1
                except (ValueError, TypeError):
                    pass
            
            ip = log.get('ip') or log.get('srcIp')
            if ip:
                ips.add(ip)
            
            duration = log.get('duration_ms') or log.get('durationMs')
            if duration is not None:
                try:
                    total_duration += float(duration)
                except (ValueError, TypeError):
                    pass
        
        avg_response = round(total_duration / total, 2) if total > 0 else 0
        error_rate = round((errors / total) * 100, 2) if total > 0 else 0
        
        return {
            'total_requests': total,
            'unique_ips': len(ips) if ips else 0,
            'avg_response_time': avg_response,
            'error_rate': error_rate,
            'success_rate': round(100 - error_rate, 2)
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
    
    # Support 'all' for cumulative
    if days == 'all':
        days = 9999  # All time
    
    try:
        return jsonify({
            'total_stats': analyzer.get_total_stats(days),
            'hourly_traffic': analyzer.get_hourly_traffic(days),
            'daily_traffic': analyzer.get_daily_traffic(days),
            'cumulative_traffic': analyzer.get_cumulative_traffic(days),
            'status_codes': analyzer.get_status_code_distribution(days),
            'popular_paths': analyzer.get_popular_paths(10, days),
            'response_times': analyzer.get_response_time_stats(days),
            'user_agents': analyzer.get_top_user_agents(5, days)
        })
    except Exception as e:
        import logging
        import traceback
        logging.getLogger('flask_access').error(f"Dashboard API error: {e}")
        logging.getLogger('flask_access').error(traceback.format_exc())
        
        return jsonify({
            'error': str(e),
            'total_stats': {'total_requests': 0, 'unique_ips': 0, 'avg_response_time': 0, 'error_rate': 0, 'success_rate': 0},
            'hourly_traffic': [{'hour': h, 'count': 0} for h in range(24)],
            'daily_traffic': [],
            'cumulative_traffic': [],
            'status_codes': [],
            'popular_paths': [],
            'response_times': {'avg': 0, 'max': 0, 'min': 0, 'p95': 0},
            'user_agents': []
        }), 500

# Add this to handle pagefind's /courses request
@dashboard_bp.route('/courses')
def courses():
    """Pagefind search endpoint - returns empty result"""
    return jsonify({'results': []}), 200