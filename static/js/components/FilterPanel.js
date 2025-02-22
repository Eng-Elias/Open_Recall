const FilterPanel = ({ filters, onFilterChange }) => {
    const handleInputChange = (field, value) => {
        onFilterChange({ ...filters, [field]: value });
    };

    return (
        <div className="filter-panel">
            <div className="filters-container">
                <div className="filter-item search-bar">
                    <label className="form-label">Search Text</label>
                    <input
                        type="text"
                        className="form-control"
                        placeholder="Search by text..."
                        value={filters.searchText || ''}
                        onChange={(e) => handleInputChange('searchText', e.target.value)}
                    />
                </div>
                
                <div className="filter-item">
                    <label className="form-label">Start Date</label>
                    <input
                        type="date"
                        className="form-control"
                        value={filters.startDate || ''}
                        onChange={(e) => handleInputChange('startDate', e.target.value)}
                    />
                </div>

                <div className="filter-item">
                    <label className="form-label">End Date</label>
                    <input
                        type="date"
                        className="form-control"
                        value={filters.endDate || ''}
                        onChange={(e) => handleInputChange('endDate', e.target.value)}
                    />
                </div>
                
                <div className="filter-item">
                    <label className="form-label">App Name</label>
                    <input
                        type="text"
                        className="form-control"
                        placeholder="Filter by app name..."
                        value={filters.appName || ''}
                        onChange={(e) => handleInputChange('appName', e.target.value)}
                    />
                </div>
                
                <div className="filter-item">
                    <div className="form-check mt-4">
                        <input
                            type="checkbox"
                            className="form-check-input"
                            checked={filters.isFavorite || false}
                            onChange={(e) => handleInputChange('isFavorite', e.target.checked)}
                        />
                        <label className="form-check-label">Show only favorites</label>
                    </div>
                </div>
            </div>
        </div>
    );
};
