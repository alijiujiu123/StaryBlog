module.exports = {
  apps: [{
    name: 'staryblog-admin',
    script: './server.js',
    cwd: './admin',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      NODE_ENV: 'production',
      PORT: 3001
    },
    error_file: './logs/admin-error.log',
    out_file: './logs/admin-out.log',
    log_file: './logs/admin-combined.log',
    time: true
  }]
};
