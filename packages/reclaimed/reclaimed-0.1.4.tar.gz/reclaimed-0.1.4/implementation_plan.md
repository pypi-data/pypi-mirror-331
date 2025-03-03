# Implementation Plan for Reclaim Performance Improvements

Based on the performance analysis, I'll implement the following high-impact changes to fix the hanging issue in interactive mode:

## 1. Adaptive UI Update Frequency

**Files to modify:**
- `reclaim/ui/textual_app.py`

**Changes:**
- Modify the `_scan_directory_worker` method to dynamically adjust the UI update interval based on the number of files scanned
- Start with frequent updates for small directories and gradually reduce frequency as more files are discovered

**Implementation:**
```python
# In textual_app.py, _scan_directory_worker method
def _scan_directory_worker(self):
    # Track when we last updated the UI
    last_ui_update = 0
    
    # Start with frequent updates, then reduce frequency as more files are discovered
    base_ui_update_interval = 0.5
    
    # Track scan progress
    scan_start_time = time.time()
    
    # Buffers to collect data between UI updates
    files_buffer = []
    dirs_buffer = []
    
    async for progress in self.scanner.scan_async(self.path):
        if not progress:
            continue
            
        # Always update our data in memory
        if progress.files:
            files_buffer = progress.files
        if progress.dirs:
            dirs_buffer = progress.dirs
            
        # Update progress bar with smoothing via the progress manager
        if hasattr(progress, 'progress'):
            self.progress_manager.update_progress(progress.progress)
        
        current_time = time.time()
        
        # Dynamically adjust update interval based on files scanned
        ui_update_interval = base_ui_update_interval
        if progress.scanned > 50000:
            ui_update_interval = 4.0  # Very infrequent updates for huge directories
        elif progress.scanned > 10000:
            ui_update_interval = 2.0  # Less frequent updates for large directories
        elif progress.scanned > 5000:
            ui_update_interval = 1.0  # Moderate updates for medium directories
        
        # Use adaptive interval between UI updates
        time_to_update = current_time - last_ui_update > ui_update_interval
        
        # Only update UI periodically or on completion
        if time_to_update or progress.progress >= 1.0:
            # Update our data
            self.largest_files = files_buffer
            self.largest_dirs = dirs_buffer
            
            # Apply sort and update tables
            self.apply_sort(self.sort_method)
            self.update_tables()
            last_ui_update = current_time
            
            # Brief yield to allow UI to update, but keep it minimal
            await asyncio.sleep(0)
```

## 2. Batch Directory Size Updates

**Files to modify:**
- `reclaim/core/scanner.py`

**Changes:**
- Modify the `_update_dir_sizes` method to batch cache updates
- Add a counter to track how many files have been processed
- Only update the cache periodically to reduce overhead

**Implementation:**
```python
# In scanner.py
def _update_dir_sizes(self, file_path: Path, file_size: int, is_icloud: bool) -> None:
    """Update directory sizes incrementally as files are processed.
    
    Args:
        file_path: Path to the file
        file_size: Size of the file in bytes
        is_icloud: Whether the file is in iCloud
    """
    # Initialize update counter if it doesn't exist
    if not hasattr(self, '_update_counter'):
        self._update_counter = 0
    self._update_counter += 1
    
    # Update size for all parent directories in memory
    for parent in file_path.parents:
        curr_size, curr_cloud = self._dir_sizes.get(parent, (0, False))
        new_size = curr_size + file_size
        new_cloud = curr_cloud or is_icloud
        self._dir_sizes[parent] = (new_size, new_cloud)
    
    # Only update cache periodically to reduce overhead
    # For large directories, update cache less frequently
    cache_update_frequency = 100
    if self._file_count > 10000:
        cache_update_frequency = 500
    elif self._file_count > 5000:
        cache_update_frequency = 250
        
    if self._update_counter % cache_update_frequency == 0:
        # Batch update the cache for all parent directories
        for parent in file_path.parents:
            size, is_cloud = self._dir_sizes.get(parent, (0, False))
            self._cache.set(parent, size, is_cloud)
```

## 3. Limit Data Processing During Scan

**Files to modify:**
- `reclaim/core/scanner.py`

**Changes:**
- Optimize the `_insert_sorted` method to avoid unnecessary insertions
- Limit the number of items tracked during scanning
- Skip insertion for items that won't make it into the final results

**Implementation:**
```python
# In scanner.py
@staticmethod
def _insert_sorted(items: List[FileInfo], item: FileInfo, max_items: int = None) -> None:
    """Insert item into sorted list maintaining size order.
    
    Args:
        items: Sorted list to insert into
        item: Item to insert
        max_items: Maximum number of items to keep (defaults to None for unlimited)
    """
    # If max_items is specified and the list is already at capacity,
    # only insert if the item is larger than the smallest item
    if max_items is not None and len(items) >= max_items and item.size <= items[-1].size:
        return  # Skip insertion for items that won't make it into the final list
        
    # Fast path for empty list or when item is smaller than all existing items
    if not items or item.size <= items[-1].size:
        items.append(item)
        # Trim if needed
        if max_items is not None and len(items) > max_items:
            items.pop()
        return
        
    # Fast path for when item is larger than all existing items
    if item.size > items[0].size:
        items.insert(0, item)
        # Trim if needed
        if max_items is not None and len(items) > max_items:
            items.pop()
        return
        
    # Binary search for insertion point
    low, high = 0, len(items) - 1
    while low <= high:
        mid = (low + high) // 2
        if items[mid].size < item.size:
            high = mid - 1
        else:
            low = mid + 1
            
    items.insert(low, item)
    
    # Trim if needed
    if max_items is not None and len(items) > max_items:
        items.pop()
```

Then update the calls to `_insert_sorted` in the `scan_async` method:

```python
# In scan_async method
# Instead of:
self._insert_sorted(largest_files, file_info)
if len(largest_files) > self.options.max_files:
    largest_files.pop()

# Use:
self._insert_sorted(largest_files, file_info, self.options.max_files)
```

## 4. Reduce Directory Size Calculation Frequency

**Files to modify:**
- `reclaim/core/scanner.py`

**Changes:**
- Increase the interval between directory size calculations
- Make the interval adaptive based on the number of files scanned

**Implementation:**
```python
# In scan_async method
# Instead of fixed interval:
dir_calc_interval = 1.0  # Calculate directory sizes once per second

# Use adaptive interval:
# Start with frequent calculations, then reduce frequency
if self._file_count > 50000:
    dir_calc_interval = 5.0  # Very infrequent for huge directories
elif self._file_count > 10000:
    dir_calc_interval = 3.0  # Less frequent for large directories
elif self._file_count > 5000:
    dir_calc_interval = 2.0  # Moderate for medium directories
else:
    dir_calc_interval = 1.0  # Frequent for small directories
```

## Implementation Strategy

I'll implement these changes in the following order:

1. First, implement the adaptive UI update frequency in `textual_app.py`
2. Next, implement the batch directory size updates in `scanner.py`
3. Then, optimize the `_insert_sorted` method and update its calls
4. Finally, implement the adaptive directory size calculation interval

After each change, I'll test the application to ensure it works correctly and verify that the performance has improved.

## Expected Outcomes

These changes should:

1. Significantly reduce the overhead of UI updates for large directories
2. Minimize the impact of directory size calculations and cache updates
3. Ensure that only the most relevant data is processed during scanning
4. Allow the interactive mode to complete successfully even for very large directories

The application should maintain its responsiveness while scanning and eventually complete the scan, just like the non-interactive mode.