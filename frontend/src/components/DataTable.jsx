import PropTypes from 'prop-types';

function DataTable ({ columns, data, onRowClick }) {
  return (
    <div className="overflow-x-auto rounded-lg border border-slate-800">
      <table className="min-w-full divide-y divide-slate-800">
        <thead className="bg-slate-900">
          <tr>
            {columns.map((column) => (
              <th key={column.accessor} className="px-4 py-2 text-left text-xs font-medium uppercase tracking-wider text-slate-400">
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800 bg-slate-900/30">
          {data.map((row) => (
            <tr
              key={row.id || JSON.stringify(row)}
              className="cursor-pointer hover:bg-slate-800/60"
              onClick={() => onRowClick?.(row)}
            >
              {columns.map((column) => (
                <td key={column.accessor} className="px-4 py-2 text-sm text-slate-100">
                  {column.render ? column.render(row[column.accessor], row) : row[column.accessor]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

DataTable.propTypes = {
  columns: PropTypes.arrayOf(
    PropTypes.shape({
      header: PropTypes.string.isRequired,
      accessor: PropTypes.string.isRequired,
      render: PropTypes.func
    })
  ).isRequired,
  data: PropTypes.arrayOf(PropTypes.object).isRequired,
  onRowClick: PropTypes.func
};

export default DataTable;
