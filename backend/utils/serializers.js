export function toJSON (value) {
  if (value === undefined || value === null) {
    return null;
  }
  return JSON.stringify(value);
}

export function fromJSON (value) {
  if (!value) return null;
  try {
    return JSON.parse(value);
  } catch (error) {
    return null;
  }
}

export function mapRows (rows, fields = []) {
  return rows.map((row) => {
    const mapped = { ...row };
    fields.forEach((field) => {
      mapped[field] = fromJSON(row[field]);
    });
    return mapped;
  });
}
