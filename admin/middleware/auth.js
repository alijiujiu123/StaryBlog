/**
 * JWT 认证中间件
 *
 * 注意：这是一个简化的实现，生产环境应该：
 * 1. 使用更强的密钥（从环境变量读取）
 * 2. 实现完整的用户管理
 * 3. 添加刷新令牌机制
 * 4. 实现请求限流
 */

const jwt = require('jsonwebtoken');

// 简化的密钥 - 生产环境应从环境变量读取
const JWT_SECRET = process.env.JWT_SECRET || 'staryblog-secret-change-in-production';

/**
 * 验证 JWT 令牌
 */
function authenticateToken(req, res, next) {
    // 获取令牌（从 Header 或查询参数）
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1] || req.query.token;

    if (!token) {
        return res.status(401).json({ error: 'Access token required' });
    }

    jwt.verify(token, JWT_SECRET, (err, user) => {
        if (err) {
            return res.status(403).json({ error: 'Invalid or expired token' });
        }
        req.user = user;
        next();
    });
}

/**
 * 生成 JWT 令牌
 */
function generateToken(user) {
    return jwt.sign(
        { username: user.username, role: user.role || 'admin' },
        JWT_SECRET,
        { expiresIn: '24h' }
    );
}

/**
 * 可选的认证（如果提供令牌则验证，否则跳过）
 */
function optionalAuth(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (token) {
        jwt.verify(token, JWT_SECRET, (err, user) => {
            if (!err) {
                req.user = user;
            }
        });
    }

    next();
}

module.exports = {
    authenticateToken,
    generateToken,
    optionalAuth,
    JWT_SECRET
};
