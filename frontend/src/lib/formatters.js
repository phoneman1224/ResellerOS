export const formatCurrency = (value, currency = 'USD') =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(Number(value || 0));

export const formatDate = (value) =>
  value ? new Intl.DateTimeFormat('en-US').format(new Date(value)) : '—';
