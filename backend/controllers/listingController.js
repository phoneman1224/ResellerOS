import {
  listListings,
  getListing,
  createListing,
  updateListing,
  deleteListing
} from '../models/listingModel.js';

export const listingController = {
  index: (_req, res) => {
    res.json(listListings());
  },
  show: (req, res) => {
    const listing = getListing(Number(req.params.id));
    if (!listing) return res.status(404).json({ message: 'Listing not found' });
    res.json(listing);
  },
  create: (req, res) => {
    res.status(201).json(createListing(req.body));
  },
  update: (req, res) => {
    const id = Number(req.params.id);
    const listing = getListing(id);
    if (!listing) return res.status(404).json({ message: 'Listing not found' });
    res.json(updateListing(id, req.body));
  },
  destroy: (req, res) => {
    const id = Number(req.params.id);
    const listing = getListing(id);
    if (!listing) return res.status(404).json({ message: 'Listing not found' });
    deleteListing(id);
    res.status(204).end();
  }
};
