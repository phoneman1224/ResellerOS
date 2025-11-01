import axios from 'axios';
import PropTypes from 'prop-types';
import { createContext, useContext, useMemo } from 'react';

const ApiContext = createContext();

const client = axios.create({
  baseURL: '/api'
});

export function ApiProvider ({ children }) {
  const value = useMemo(() => ({
    client,
    async list (resource) {
      const { data } = await client.get(`/${resource}`);
      return data;
    },
    async create (resource, payload) {
      const { data } = await client.post(`/${resource}`, payload);
      return data;
    },
    async update (resource, id, payload) {
      const { data } = await client.put(`/${resource}/${id}`, payload);
      return data;
    },
    async remove (resource, id) {
      await client.delete(`/${resource}/${id}`);
    }
  }), []);

  return (
    <ApiContext.Provider value={value}>
      {children}
    </ApiContext.Provider>
  );
}

ApiProvider.propTypes = {
  children: PropTypes.node
};

export const useApi = () => useContext(ApiContext);
