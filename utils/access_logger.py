# access_logger.py
import json
import time
import os
import logging
from datetime import datetime
from functools import wraps
from flask import request, g
from pathlib import Path

class AccessLogger:
    """Unified access log collector for Flask applications"""
    
    def __init__(self, app=None, log_dir='logs', log_format='json'):
        self.log_dir = Path(log_dir)
        self.log_format = log_format  # 'json' or 'line'
        self.logger = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(exist_ok=True, parents=True)
        
        # Set up file handlers
        access_log_path = self.log_dir / 'access.log'
        error_log_path = self.log_dir / 'error.log'
        
        # Create logger
        self.logger = logging.getLogger('flask_access')
        self.logger.setLevel(logging.INFO)
        
        # Access log handler (INFO level)
        access_handler = logging.FileHandler(access_log_path)
        access_handler.setLevel(logging.INFO)
        
        # Error log handler (WARNING and above)
        error_handler = logging.FileHandler(error_log_path)
        error_handler.setLevel(logging.WARNING)
        
        # Formatter based on format type
        if self.log_format == 'json':
            access_handler.setFormatter(JsonFormatter())
        else:
            access_handler.setFormatter(logging.Formatter('%(message)s'))
        
        error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        
        self.logger.addHandler(access_handler)
        self.logger.addHandler(error_handler)
        
        # Store for later use
        app.access_logger = self
        
        # Register before/after request handlers
        @app.before_request
        def before_request():
            g.request_start_time = time.perf_counter()
        
        @app.after_request
        def after_request(response):
            self.log_request(response)
            return response
    
    def anonymize_ip(self, ip):
        """Anonymize IP address by zeroing out the last octet"""
        if not ip:
            return None
        if '.' in ip:  # IPv4
            parts = ip.split('.')
            if len(parts) == 4:
                return '.'.join(parts[:-1] + ['0'])
        elif ':' in ip:  # IPv6 - simplified anonymization
            return ip.split(':')[0] + '::'
        return ip
    
    def log_request(self, response):
        """Log request data after response is generated"""
        if not self.logger:
            return
        
        # Calculate duration
        start_time = getattr(g, 'request_start_time', None)
        duration_ms = 0
        if start_time:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        
        # Get client IP (handles proxies)
        client_ip = request.remote_addr
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            client_ip = forwarded_for.split(',')[0].strip()
        
        # Build log data
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'ip': self.anonymize_ip(client_ip),
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code,
            'duration_ms': duration_ms,
            'user_agent': request.headers.get('User-Agent', '')[:500],
            'referrer': request.referrer,
            'query_string': request.query_string.decode('utf-8')[:200] if request.query_string else '',
            'content_length': request.content_length or 0,
        }
        
        # Log based on status code
        if response.status_code >= 400:
            self.logger.warning(json.dumps(log_data))
        else:
            self.logger.info(json.dumps(log_data))
    
    def get_stats(self, days=7):
        """Simple statistics from log files (optional utility)"""
        import re
        from collections import Counter, defaultdict
        
        stats = {
            'total_requests': 0,
            'avg_duration_ms': 0,
            'status_counts': Counter(),
            'top_paths': Counter(),
            'errors': []
        }
        
        log_file = self.log_dir / 'access.log'
        if not log_file.exists():
            return stats
        
        durations = []
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    stats['total_requests'] += 1
                    stats['status_counts'][data['status_code']] += 1
                    stats['top_paths'][data['path']] += 1
                    durations.append(data['duration_ms'])
                    
                    if data['status_code'] >= 400:
                        stats['errors'].append(data)
                except:
                    continue
        
        if durations:
            stats['avg_duration_ms'] = round(sum(durations) / len(durations), 2)
        
        return stats


class JsonFormatter(logging.Formatter):
    """Custom formatter to output JSON"""
    def format(self, record):
        if isinstance(record.msg, dict):
            return json.dumps(record.msg)
        return record.getMessage()