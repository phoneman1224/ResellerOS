import { getSettings, setSettings } from '../models/settingsModel.js';

export const settingsController = {
  show: (_req, res) => {
    res.json(getSettings());
  },
  update: (req, res) => {
    res.json(setSettings(req.body));
  }
};
