const ScreenshotGrid = ({
  screenshots,
  allTags,
  onToggleFavorite,
  onAddTag,
  onRemoveTag,
  currentPage,
  onPageChange,
}) => {
  const renderPaginationItem = (pageNum) => (
    <li
      key={pageNum}
      className={`page-item ${screenshots.page === pageNum ? "active" : ""}`}
    >
      <button className="page-link" onClick={() => onPageChange(pageNum)}>
        {pageNum}
      </button>
    </li>
  );

  const renderPagination = () => {
    if (!screenshots || screenshots.pages <= 1) return null;

    const currentPage = screenshots.page;
    const totalPages = screenshots.pages;
    let pages = [];

    // Always add first page
    pages.push(1);

    // Add ellipsis after first page if needed
    if (currentPage > 3) {
      pages.push('...');
    }

    // Add pages around current page
    for (let i = Math.max(2, currentPage - 1); i <= Math.min(totalPages - 1, currentPage + 1); i++) {
      if (i === currentPage - 1 || i === currentPage || i === currentPage + 1) {
        pages.push(i);
      }
    }

    // Add ellipsis before last page if needed
    if (currentPage < totalPages - 2) {
      pages.push('...');
    }

    // Always add last page if not already included
    if (totalPages > 1 && !pages.includes(totalPages)) {
      pages.push(totalPages);
    }

    // Remove duplicate ellipsis
    pages = pages.filter((page, index, array) => {
      if (page === '...') {
        return array[index - 1] !== '...';
      }
      return true;
    });

    return (
      <nav className="mt-4">
        <ul className="pagination">
          <li className={`page-item ${currentPage === 1 ? "disabled" : ""}`}>
            <button
              className="page-link"
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage === 1}
            >
              ←
            </button>
          </li>
          {pages.map((page, index) =>
            page === '...' ? (
              <li key={`ellipsis-${index}`} className="page-item disabled">
                <span className="page-link">...</span>
              </li>
            ) : (
              renderPaginationItem(page)
            )
          )}
          <li
            className={`page-item ${
              currentPage === totalPages ? "disabled" : ""
            }`}
          >
            <button
              className="page-link"
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              →
            </button>
          </li>
        </ul>
      </nav>
    );
  };

  return (
    <div>
      <div className="row g-4">
        {screenshots?.items?.map((screenshot) => (
          <div key={screenshot.id} className="col-md-4">
            <div className="card screenshot-card">
              <img
                src={`/assets/${screenshot.file_path}`}
                className="card-img-top"
                alt="Screenshot"
              />
              <div className="card-body">
                <div className="d-flex justify-content-between align-items-start mb-2">
                  <h6 className="card-title">{screenshot.app_name}</h6>
                  <span
                    className="favorite-icon"
                    onClick={() => onToggleFavorite(screenshot.id)}
                  >
                    {screenshot.is_favorite ? "★" : "☆"}
                  </span>
                </div>
                <p className="card-text small text-muted">
                  {new Date(screenshot.timestamp).toLocaleString()}
                </p>
                <div className="tags-container">
                  {screenshot.tags.map((tag) => (
                    <span
                      key={tag.id}
                      className="badge bg-secondary me-1 mb-1"
                      onClick={() => onRemoveTag(screenshot.id, tag.id)}
                      style={{ cursor: "pointer" }}
                    >
                      {tag.name} ×
                    </span>
                  ))}
                  <div className="dropdown d-inline-block">
                    <button
                      className="btn btn-sm btn-outline-secondary dropdown-toggle"
                      type="button"
                      data-bs-toggle="dropdown"
                    >
                      + Add Tag
                    </button>
                    <ul className="dropdown-menu">
                      {allTags
                        .filter(
                          (tag) =>
                            !screenshot.tags.some(
                              (screenshotTag) => screenshotTag.id === tag.id
                            )
                        )
                        .map((tag) => (
                          <li key={tag.id}>
                            <a
                              className="dropdown-item"
                              href="#"
                              onClick={(e) => {
                                e.preventDefault();
                                onAddTag(screenshot.id, tag.id);
                              }}
                            >
                              {tag.name}
                            </a>
                          </li>
                        ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
      {renderPagination()}
    </div>
  );
};
