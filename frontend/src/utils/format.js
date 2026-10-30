import { format, formatDistanceToNow } from "date-fns";
import { es } from "date-fns/locale";

export const formatDate = (value, pattern = "dd/MM/yyyy HH:mm") =>
  value ? format(new Date(value), pattern, { locale: es }) : "—";

export const timeAgo = (value) =>
  value ? formatDistanceToNow(new Date(value), { addSuffix: true, locale: es }) : "—";

export const percent = (value) => `${Math.round((value || 0) * 100)}%`;
