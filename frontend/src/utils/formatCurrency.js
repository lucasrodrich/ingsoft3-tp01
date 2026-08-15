export const formatCurrency = (value) => new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS" }).format(Number(value || 0));

