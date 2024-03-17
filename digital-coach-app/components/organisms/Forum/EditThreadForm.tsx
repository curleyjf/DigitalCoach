import React, { useState } from 'react';
import Button from '../../atoms/Button';

function EditThreadForm({ initialTitle, initialContent, onSubmit }) {
  const [title, setTitle] = useState(initialTitle);
  const [content, setContent] = useState(initialContent);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(title, content);
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Edit Thread</h2>
      <div>
        <label>Title:</label>
        <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} required />
      </div>
      <div>
        <label>Content:</label>
        <textarea value={content} onChange={(e) => setContent(e.target.value)} required />
      </div>
      <Button type="submit">Submit</Button>
    </form>
  );
}

export default EditThreadForm;