const TagManager = ({
  selectedTagIds,
  allTags,
  onTagSelect,
  onTagsUpdate,
  onDeleteTag,
}) => {
  const [newTagName, setNewTagName] = React.useState("");
  const [showConfirmDelete, setShowConfirmDelete] = React.useState(null);

  const handleCreateTag = async (e) => {
    e.preventDefault();
    if (newTagName.trim()) {
      try {
        const response = await fetch("/api/tags", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ name: newTagName.trim() }),
        });

        if (response.ok) {
          await onTagsUpdate();
          setNewTagName("");
        }
      } catch (error) {
        console.error("Error creating tag:", error);
      }
    }
  };

  const confirmDeleteTag = (tagId) => {
    setShowConfirmDelete(tagId);
  };

  const cancelDeleteTag = () => {
    setShowConfirmDelete(null);
  };

  const deleteTag = async (tagId) => {
    await onDeleteTag(tagId);
    setShowConfirmDelete(null);
  };

  return (
    <div className="tag-manager mb-4">
      <div className="card">
        <div className="card-body">
          <div className="d-flex align-items-center gap-3 mb-3">
            <h5 className="card-title mb-0">Tags</h5>
            <form
              onSubmit={handleCreateTag}
              className="d-flex gap-2 flex-grow-1"
            >
              <input
                type="text"
                className="form-control form-control-sm"
                placeholder="New tag name..."
                value={newTagName}
                onChange={(e) => setNewTagName(e.target.value)}
              />
              <button type="submit" className="btn btn-sm btn-primary">
                Add
              </button>
            </form>
          </div>

          <div className="d-flex gap-2 flex-wrap">
            {allTags.map((tag) => (
              <div
                key={tag.id}
                className="tag-item d-inline-flex align-items-center"
              >
                <span
                  className={`badge ${
                    selectedTagIds.includes(tag.id)
                      ? "bg-primary"
                      : "bg-secondary"
                  } tag-badge`}
                  onClick={() => onTagSelect(tag.id)}
                  style={{ cursor: "pointer" }}
                >
                  {tag.name}
                </span>

                {showConfirmDelete === tag.id ? (
                  <div className="ms-1 d-inline-flex">
                    <button
                      className="btn btn-danger btn-sm py-0 px-1 me-1"
                      onClick={() => deleteTag(tag.id)}
                      title="Confirm delete"
                    >
                      <small>✓</small>
                    </button>
                    <button
                      className="btn btn-secondary btn-sm py-0 px-1"
                      onClick={cancelDeleteTag}
                      title="Cancel"
                    >
                      <small>✕</small>
                    </button>
                  </div>
                ) : (
                  <button
                    className="btn btn-sm text-danger ms-1 p-0"
                    onClick={() => confirmDeleteTag(tag.id)}
                    title="Delete tag"
                    style={{ fontSize: "0.8rem" }}
                  >
                    ×
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
