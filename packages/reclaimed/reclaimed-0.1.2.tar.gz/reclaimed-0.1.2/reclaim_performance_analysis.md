# Reclaim Disk Scanner Performance Analysis

## Problem Statement
The Reclaim disk scanner Python application hangs when run in interactive mode on very large directories, despite initially progressing quickly and displaying the largest folders and files. The scan never completes, uses large amounts of disk I/O, and slows down the computer, even though the non-interactive mode completes successfully.

## Analysis of Code Structure

After reviewing the codebase, I've identified the key components:

1. **Core Scanner (`scanner.py`)**: Contains the main scanning logic with both synchronous and asynchronous implementations
2. **CLI Interface (`cli.py`)**: Handles command-line arguments and launches either interactive or non-interactive mode
3. **Interactive UI (`textual_app.py`)**: Implements the Textual-based UI with real-time updates
4. **Supporting Components**:
   - `types.py`: Defines data structures
   - `cache.py`: Implements directory size caching
   - `filesystem.py`: Provides optimized filesystem operations

## Key Differences Between Interactive and Non-Interactive Modes

| Feature | Interactive Mode | Non-Interactive Mode |
|---------|-----------------|---------------------|
| Implementation | Uses `run_textual_ui()` with Textual UI | Uses `scanner.scan()` synchronously |
| Scanning Method | `scan_async()` with progress updates | `scan()` with complete results at end |
| Directory Traversal | `_walk_directory_async()` with async yields | `_walk_directory()` with synchronous recursion |
| UI Updates | Real-time updates during scanning | Single display after completion |

## Identified Performance Issues

### 1. Excessive UI Updates and Rendering

```python
# In textual_app.py, line 287
ui_update_interval = 0.5  # Only update UI twice per second
```

The UI is updated every 0.5 seconds, which includes:
- Sorting large file/directory lists
- Updating data tables
- Rendering the UI

For very large directories, these frequent updates become increasingly expensive.

### 2. Redundant Directory Size Calculations

```python
# In scanner.py, lines 118-121
current_time = time.time()
if current_time - last_dir_calc_time >= dir_calc_interval:
    # Get largest directories
    largest_dirs = self._get_largest_dirs(root_path)
    last_dir_calc_time = current_time
```

Directory sizes are recalculated every second, which is expensive for large directory structures.

### 3. Inefficient Parent Directory Size Updates

```python
# In scanner.py, lines 317-334
def _update_dir_sizes(self, file_path: Path, file_size: int, is_icloud: bool) -> None:
    # Update size for all parent directories
    for parent in file_path.parents:
        curr_size, curr_cloud = self._dir_sizes.get(parent, (0, False))
        new_size = curr_size + file_size
        new_cloud = curr_cloud or is_icloud
        self._dir_sizes[parent] = (new_size, new_cloud)
        
        # Cache the result for future scans
        self._cache.set(parent, new_size, new_cloud)
```

For deeply nested directories, this updates and caches sizes for all parent directories for every file, which becomes extremely expensive in large directory structures.

### 4. Asyncio Event Loop Starvation

```python
# In scanner.py, lines 261-262
if not is_small_directory and processed_count % 500 == 0:
    await asyncio.sleep(0)
```

The `await asyncio.sleep(0)` calls yield control to the event loop, but in large directories, this might cause the event loop to prioritize UI updates over completing the scan.

### 5. Excessive Sorting Operations

```python
# In textual_app.py, lines 322-323
# Apply sort and update tables
self.apply_sort(self.sort_method)
self.update_tables()
```

Sorting is performed on each UI update, which becomes expensive for large lists.

## Root Cause Analysis

The primary issue appears to be a **feedback loop** between scanning and UI updates:

1. As the directory size grows, each UI update becomes more expensive
2. The async scanning yields control frequently to update the UI
3. This slows down the actual scanning progress
4. More files are discovered, making UI updates even more expensive
5. Eventually, the system spends most of its time updating the UI rather than completing the scan

This explains why:
- The scan initially progresses quickly (when there's little data to display)
- It shows the largest folders and files (partial results are displayed)
- It ultimately hangs (the feedback loop becomes overwhelming)
- Non-interactive mode works fine (no UI updates to slow it down)

## Proposed Solutions

### 1. Adaptive UI Update Frequency

Dynamically adjust the UI update frequency based on the number of files scanned:

```python
# In textual_app.py
def _scan_directory_worker(self):
    # ...
    # Start with frequent updates
    ui_update_interval = 0.5
    
    # Track files processed
    files_processed = 0
    
    async for progress in self.scanner.scan_async(self.path):
        # ...
        files_processed = progress.scanned
        
        # Dynamically adjust update interval based on files processed
        if files_processed > 10000:
            ui_update_interval = 2.0
        elif files_processed > 5000:
            ui_update_interval = 1.0
        # ...
```

### 2. Batch Directory Size Updates

Modify the `_update_dir_sizes` method to batch updates to parent directories:

```python
def _update_dir_sizes(self, file_path: Path, file_size: int, is_icloud: bool) -> None:
    # Use a counter to track how many files we've processed
    self._update_counter = getattr(self, '_update_counter', 0) + 1
    
    # Update parent directories
    for parent in file_path.parents:
        curr_size, curr_cloud = self._dir_sizes.get(parent, (0, False))
        new_size = curr_size + file_size
        new_cloud = curr_cloud or is_icloud
        self._dir_sizes[parent] = (new_size, new_cloud)
    
    # Only update cache periodically to reduce overhead
    if self._update_counter % 100 == 0:
        for parent in file_path.parents:
            size, is_cloud = self._dir_sizes.get(parent, (0, False))
            self._cache.set(parent, size, is_cloud)
```

### 3. Progressive Scanning Strategy

Implement a two-phase scanning approach:

```python
async def scan_async(self, root_path: Path) -> AsyncIterator[ScanProgress]:
    # Phase 1: Quick scan with minimal updates
    phase = "quick"
    chunk_size = 1000  # Process more files between updates
    ui_update_interval = 2.0  # Less frequent updates
    
    # ... scanning logic ...
    
    # After processing a certain number of files, switch to detailed phase
    if self._file_count > 10000 and phase == "quick":
        phase = "detailed"
        # Yield a progress update indicating phase change
        yield ScanProgress(
            progress=0.5,  # Indicate halfway through
            files=largest_files[:self.options.max_files],
            dirs=largest_dirs[:self.options.max_dirs],
            scanned=self._file_count,
            total_size=self._total_size,
            phase=phase
        )
```

### 4. Limit Data Processing During Scan

Only track a fixed number of largest files/directories during scanning:

```python
def _insert_sorted(items: List[FileInfo], item: FileInfo, max_items: int) -> None:
    """Insert item into sorted list maintaining size order, limited to max_items."""
    # Fast path for empty list
    if not items:
        items.append(item)
        return
        
    # If list is at capacity and item is smaller than smallest item, skip
    if len(items) >= max_items and item.size <= items[-1].size:
        return
        
    # ... insertion logic ...
    
    # Trim list if needed
    if len(items) > max_items:
        items.pop()
```

### 5. Implement Scan Timeout

Add a timeout mechanism for very large directories:

```python
async def scan_async(self, root_path: Path) -> AsyncIterator[ScanProgress]:
    # ...
    start_time = time.time()
    max_scan_time = 120  # 2 minutes max for interactive mode
    
    async for path, is_file, size in self._walk_directory_async(root_path):
        # Check if we've exceeded the time limit
        if time.time() - start_time > max_scan_time:
            # Yield final progress with timeout indicator
            yield ScanProgress(
                progress=0.9,  # Indicate mostly complete
                files=largest_files[:self.options.max_files],
                dirs=largest_dirs[:self.options.max_dirs],
                scanned=self._file_count,
                total_size=self._total_size,
                timed_out=True
            )
            return
        # ... rest of scanning logic ...
```

## Implementation Recommendations

I recommend implementing these changes in the following order:

1. **Quick Wins**:
   - Adaptive UI update frequency
   - Limit data processing during scan

2. **Medium Effort**:
   - Batch directory size updates
   - Implement scan timeout

3. **Larger Changes**:
   - Progressive scanning strategy
   - Redesign the async scanning logic

## Testing Strategy

To validate these changes:

1. Create test directories of varying sizes (small, medium, large)
2. Benchmark both interactive and non-interactive modes before and after changes
3. Monitor system resources (CPU, memory, disk I/O) during scans
4. Verify that interactive mode completes within a reasonable time for large directories

## Conclusion

The performance issues in the Reclaim disk scanner's interactive mode stem from a feedback loop between scanning and UI updates. By implementing the proposed solutions, we can break this loop and ensure that the scanner completes successfully even for very large directories.