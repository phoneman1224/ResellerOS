import {
  listSales,
  getSale,
  createSale,
  updateSale,
  deleteSale
} from '../models/saleModel.js';

export const saleController = {
  index: (_req, res) => {
    res.json(listSales());
  },
  show: (req, res) => {
    const sale = getSale(Number(req.params.id));
    if (!sale) return res.status(404).json({ message: 'Sale not found' });
    res.json(sale);
  },
  create: (req, res) => {
    res.status(201).json(createSale(req.body));
  },
  update: (req, res) => {
    const id = Number(req.params.id);
    const sale = getSale(id);
    if (!sale) return res.status(404).json({ message: 'Sale not found' });
    res.json(updateSale(id, req.body));
  },
  destroy: (req, res) => {
    const id = Number(req.params.id);
    const sale = getSale(id);
    if (!sale) return res.status(404).json({ message: 'Sale not found' });
    deleteSale(id);
    res.status(204).end();
  }
};
