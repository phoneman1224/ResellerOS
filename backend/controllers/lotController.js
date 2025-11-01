import {
  listLots,
  getLot,
  createLot,
  updateLot,
  deleteLot
} from '../models/lotModel.js';

export const lotController = {
  index: (_req, res) => {
    res.json(listLots());
  },
  show: (req, res) => {
    const lot = getLot(Number(req.params.id));
    if (!lot) return res.status(404).json({ message: 'Lot not found' });
    res.json(lot);
  },
  create: (req, res) => {
    res.status(201).json(createLot(req.body));
  },
  update: (req, res) => {
    const id = Number(req.params.id);
    const lot = getLot(id);
    if (!lot) return res.status(404).json({ message: 'Lot not found' });
    res.json(updateLot(id, req.body));
  },
  destroy: (req, res) => {
    const id = Number(req.params.id);
    const lot = getLot(id);
    if (!lot) return res.status(404).json({ message: 'Lot not found' });
    deleteLot(id);
    res.status(204).end();
  }
};
