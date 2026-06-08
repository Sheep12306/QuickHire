import api from '../index'

// Packages
export function getPackages() { return api.get('/admin/packages/plans') }
export function createPackage(data) { return api.post('/admin/packages/plans', data) }
export function updatePackage(id, data) { return api.put(`/admin/packages/plans/${id}`, data) }
export function deletePackage(id) { return api.delete(`/admin/packages/plans/${id}`) }

// Orders
export function getOrders(params = {}) { return api.get('/admin/packages/orders', { params }) }
export function refundOrder(id, reason = '') { return api.post(`/admin/packages/orders/${id}/refund`, { reason }) }

// Memberships
export function getMemberships(params = {}) { return api.get('/admin/packages/memberships', { params }) }
export function extendMembership(userId, days = 30) { return api.post(`/admin/packages/memberships/${userId}/extend`, null, { params: { days } }) }
export function cancelMembership(userId) { return api.post(`/admin/packages/memberships/${userId}/cancel`) }
