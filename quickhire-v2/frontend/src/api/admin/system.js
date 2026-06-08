import api from '../index'

export function getSystemConfig() { return api.get('/admin/system/config') }
export function updateSystemConfig(items) { return api.put('/admin/system/config', items) }
export function getRoles() { return api.get('/admin/system/roles') }
export function getIpWhitelist() { return api.get('/admin/system/ip-whitelist') }
export function updateIpWhitelist(data) { return api.put('/admin/system/ip-whitelist', data) }
export function getSystemAuditLog(params = {}) { return api.get('/admin/system/audit-log', { params }) }
