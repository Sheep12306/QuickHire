import api from '../index'

// Resume Templates
export function getTemplates(params = {}) { return api.get('/admin/content/templates', { params }) }
export function createTemplate(data) { return api.post('/admin/content/templates', data) }
export function updateTemplate(id, data) { return api.put(`/admin/content/templates/${id}`, data) }
export function deleteTemplate(id) { return api.delete(`/admin/content/templates/${id}`) }

// Prompt Templates
export function getPrompts(params = {}) { return api.get('/admin/content/prompts', { params }) }
export function createPrompt(data) { return api.post('/admin/content/prompts', data) }
export function updatePrompt(id, data) { return api.put(`/admin/content/prompts/${id}`, data) }
export function deletePrompt(id) { return api.delete(`/admin/content/prompts/${id}`) }

// Announcements
export function getAnnouncements(params = {}) { return api.get('/admin/content/announcements', { params }) }
export function createAnnouncement(data) { return api.post('/admin/content/announcements', data) }
export function updateAnnouncement(id, data) { return api.put(`/admin/content/announcements/${id}`, data) }
export function deleteAnnouncement(id) { return api.delete(`/admin/content/announcements/${id}`) }

// Help Articles
export function getHelpArticles(params = {}) { return api.get('/admin/content/help', { params }) }
export function createHelpArticle(data) { return api.post('/admin/content/help', data) }
export function updateHelpArticle(id, data) { return api.put(`/admin/content/help/${id}`, data) }
export function deleteHelpArticle(id) { return api.delete(`/admin/content/help/${id}`) }
