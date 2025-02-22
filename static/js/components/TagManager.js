const TagManager = ({ selectedTags, allTags, onTagSelect, onTagCreate }) => {
  const [newTagName, setNewTagName] = React.useState("");

  const handleCreateTag = async (e) => {
    e.preventDefault();
    if (newTagName.trim()) {
      await onTagCreate(newTagName.trim());
      setNewTagName("");
    }
  };

  return (
    <div className="tag-manager">
      <div className="d-flex align-items-center gap-3">
        <div className="flex-grow-1">
          <div className="d-flex gap-2 flex-wrap">
            <h5>Tags</h5>
            {allTags.map((tag) => (
              <span
                key={tag.id}
                className={`badge ${
                  selectedTags.includes(tag.id) ? "bg-primary" : "bg-secondary"
                } tag-badge`}
                onClick={() => onTagSelect(tag.id)}
              >
                {tag.name}
              </span>
            ))}
          </div>
        </div>
        <form onSubmit={handleCreateTag} className="d-flex gap-2 flex-shrink-0">
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
    </div>
  );
};
