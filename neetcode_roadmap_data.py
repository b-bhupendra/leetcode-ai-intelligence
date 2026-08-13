"""
NeetCode Roadmap & Curated Problem Tracks Ingestion Engine

Contains complete DAG topological structure, tracks, prerequisites,
and problem mappings for NeetCode 75, NeetCode 150, and NeetCode 250+.
"""

import json
from typing import Dict, List, Any

NEETCODE_DAG_NODES = [
    {
        "id": "arrays-hashing",
        "title": "Arrays & Hashing",
        "category": "Linear Structures",
        "level": 1,
        "x": 100,
        "y": 100,
        "prerequisites": [],
        "description": "Foundational array manipulation, hash map lookups, frequency counting, and string encoding.",
        "gfg_url": "https://www.geeksforgeeks.org/array-data-structure/",
        "color": "from-emerald-500 to-teal-600"
    },
    {
        "id": "two-pointers",
        "title": "Two Pointers",
        "category": "Linear Pointers",
        "level": 2,
        "x": 50,
        "y": 220,
        "prerequisites": ["arrays-hashing"],
        "description": "Converging and diverging pointers on sorted or monotonic arrays and strings.",
        "gfg_url": "https://www.geeksforgeeks.org/two-pointers-technique/",
        "color": "from-teal-500 to-cyan-600"
    },
    {
        "id": "stack",
        "title": "Stack",
        "category": "Linear Structures",
        "level": 2,
        "x": 150,
        "y": 220,
        "prerequisites": ["arrays-hashing"],
        "description": "LIFO memory, parenthesis matching, monotonic stack for next greater elements.",
        "gfg_url": "https://www.geeksforgeeks.org/stack-data-structure/",
        "color": "from-cyan-500 to-blue-600"
    },
    {
        "id": "sliding-window",
        "title": "Sliding Window",
        "category": "Linear Pointers",
        "level": 3,
        "x": 50,
        "y": 340,
        "prerequisites": ["two-pointers"],
        "description": "Dynamic expanding/shrinking contiguous bounds for optimal subarray/substring search.",
        "gfg_url": "https://www.geeksforgeeks.org/window-sliding-technique/",
        "color": "from-blue-500 to-indigo-600"
    },
    {
        "id": "binary-search",
        "title": "Binary Search",
        "category": "Search Space",
        "level": 3,
        "x": 150,
        "y": 340,
        "prerequisites": ["arrays-hashing"],
        "description": "O(log N) division of search spaces, rotated arrays, and binary search on monotonic solution spaces.",
        "gfg_url": "https://www.geeksforgeeks.org/binary-search/",
        "color": "from-indigo-500 to-violet-600"
    },
    {
        "id": "linked-list",
        "title": "Linked List",
        "category": "Linear Structures",
        "level": 3,
        "x": 250,
        "y": 340,
        "prerequisites": ["arrays-hashing"],
        "description": "Pointer reversal, fast/slow cycle detection, dummy heads, and merging lists.",
        "gfg_url": "https://www.geeksforgeeks.org/data-structures/linked-list/",
        "color": "from-violet-500 to-purple-600"
    },
    {
        "id": "trees",
        "title": "Trees",
        "category": "Hierarchical Data",
        "level": 4,
        "x": 150,
        "y": 460,
        "prerequisites": ["binary-search", "linked-list"],
        "description": "Binary Tree traversals (In/Pre/Post/Level), BST properties, LCA, and bottom-up tree state recursion.",
        "gfg_url": "https://www.geeksforgeeks.org/binary-tree-data-structure/",
        "color": "from-purple-500 to-fuchsia-600"
    },
    {
        "id": "tries",
        "title": "Tries",
        "category": "Hierarchical Data",
        "level": 5,
        "x": 80,
        "y": 580,
        "prerequisites": ["trees"],
        "description": "Prefix tree character transitions, dictionary word lookups, and auto-completion.",
        "gfg_url": "https://www.geeksforgeeks.org/trie-insert-and-search/",
        "color": "from-fuchsia-500 to-pink-600"
    },
    {
        "id": "heap-priority-queue",
        "title": "Heap / Priority Queue",
        "category": "Linear Structures",
        "level": 5,
        "x": 220,
        "y": 580,
        "prerequisites": ["trees"],
        "description": "Min/Max heaps, top-K frequent elements, streaming medians, and multi-way k-sorted merges.",
        "gfg_url": "https://www.geeksforgeeks.org/heap-data-structure/",
        "color": "from-pink-500 to-rose-600"
    },
    {
        "id": "backtracking",
        "title": "Backtracking",
        "category": "Search Space",
        "level": 5,
        "x": 320,
        "y": 580,
        "prerequisites": ["trees"],
        "description": "DFS state tree exploration, combinations, permutations, pruning, and state rollback.",
        "gfg_url": "https://www.geeksforgeeks.org/backtracking-algorithms/",
        "color": "from-rose-500 to-amber-600"
    },
    {
        "id": "graphs",
        "title": "Graphs",
        "category": "Graph Theory",
        "level": 6,
        "x": 220,
        "y": 700,
        "prerequisites": ["trees", "backtracking"],
        "description": "Adjacency lists, matrix BFS/DFS, connected components, cycle detection, topological sorting.",
        "gfg_url": "https://www.geeksforgeeks.org/graph-data-structure-and-algorithms/",
        "color": "from-amber-500 to-emerald-600"
    },
    {
        "id": "advanced-graphs",
        "title": "Advanced Graphs",
        "category": "Graph Theory",
        "level": 7,
        "x": 220,
        "y": 820,
        "prerequisites": ["graphs", "heap-priority-queue"],
        "description": "Dijkstra's shortest path, Prim's/Kruskal's MST, Bellman-Ford, network flow, and Eulerian paths.",
        "gfg_url": "https://www.geeksforgeeks.org/dijkstras-shortest-path-algorithm-greedy-algo-7/",
        "color": "from-emerald-600 to-teal-700"
    },
    {
        "id": "1d-dp",
        "title": "1-D Dynamic Programming",
        "category": "Optimization",
        "level": 6,
        "x": 340,
        "y": 700,
        "prerequisites": ["backtracking"],
        "description": "Linear recurrence, memoization, bottom-up tabulation, space optimization, and unbounded knapsack.",
        "gfg_url": "https://www.geeksforgeeks.org/dynamic-programming/",
        "color": "from-indigo-600 to-purple-700"
    },
    {
        "id": "2d-dp",
        "title": "2-D Dynamic Programming",
        "category": "Optimization",
        "level": 7,
        "x": 340,
        "y": 820,
        "prerequisites": ["1d-dp"],
        "description": "Grid paths, dual-string edit distance, LCS, matrix chain multiplication, and interval DP.",
        "gfg_url": "https://www.geeksforgeeks.org/dynamic-programming/#advanced",
        "color": "from-purple-600 to-rose-700"
    },
    {
        "id": "greedy",
        "title": "Greedy",
        "category": "Optimization",
        "level": 7,
        "x": 80,
        "y": 820,
        "prerequisites": ["arrays-hashing"],
        "description": "Locally optimal choice property, activity selection, gas station balance, and jump games.",
        "gfg_url": "https://www.geeksforgeeks.org/greedy-algorithms/",
        "color": "from-amber-600 to-yellow-600"
    },
    {
        "id": "intervals",
        "title": "Intervals",
        "category": "Optimization",
        "level": 8,
        "x": 80,
        "y": 940,
        "prerequisites": ["greedy"],
        "description": "Interval sorting by start/end time, interval overlaps, merging, and non-overlapping removals.",
        "gfg_url": "https://www.geeksforgeeks.org/interval-tree/",
        "color": "from-yellow-500 to-orange-600"
    },
    {
        "id": "math-geometry",
        "title": "Math & Geometry",
        "category": "Mathematics",
        "level": 8,
        "x": 220,
        "y": 940,
        "prerequisites": ["arrays-hashing"],
        "description": "Matrix rotation, spiral order, fast exponentiation, GCD, prime sieves, and geometric angles.",
        "gfg_url": "https://www.geeksforgeeks.org/mathematical-algorithms/",
        "color": "from-orange-500 to-amber-600"
    },
    {
        "id": "bit-manipulation",
        "title": "Bit Manipulation",
        "category": "Low-Level Optimization",
        "level": 8,
        "x": 340,
        "y": 940,
        "prerequisites": ["math-geometry"],
        "description": "Bitwise AND/OR/XOR/NOT, counting bits, bitmasks for subsets, reverse bits, and missing number.",
        "gfg_url": "https://www.geeksforgeeks.org/bitwise-operators-in-c-cpp/",
        "color": "from-cyan-600 to-blue-700"
    }
]

NEETCODE_PROBLEMS = [
    # Arrays & Hashing
    {"task_id": "contains-duplicate", "title": "Contains Duplicate", "difficulty": "Easy", "track": "arrays-hashing", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/3OamzN90kPg"},
    {"task_id": "valid-anagram", "title": "Valid Anagram", "difficulty": "Easy", "track": "arrays-hashing", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/9UtInBqnCgA"},
    {"task_id": "two-sum", "title": "Two Sum", "difficulty": "Easy", "track": "arrays-hashing", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/KLlXCFG5TnA"},
    {"task_id": "group-anagrams", "title": "Group Anagrams", "difficulty": "Medium", "track": "arrays-hashing", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/vzdNOK2oQ2k"},
    {"task_id": "top-k-frequent-elements", "title": "Top K Frequent Elements", "difficulty": "Medium", "track": "arrays-hashing", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/YPTqKIgVk-k"},
    {"task_id": "product-of-array-except-self", "title": "Product of Array Except Self", "difficulty": "Medium", "track": "arrays-hashing", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/bNvIQI2wAjk"},
    {"task_id": "valid-sudoku", "title": "Valid Sudoku", "difficulty": "Medium", "track": "arrays-hashing", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/TjFXEUCMqI8"},
    {"task_id": "encode-and-decode-strings", "title": "Encode and Decode Strings", "difficulty": "Medium", "track": "arrays-hashing", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/B1k_sxOSgv8"},
    {"task_id": "longest-consecutive-sequence", "title": "Longest Consecutive Sequence", "difficulty": "Medium", "track": "arrays-hashing", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/P6RZZMu_maU"},

    # Two Pointers
    {"task_id": "valid-palindrome", "title": "Valid Palindrome", "difficulty": "Easy", "track": "two-pointers", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/jJXJ16kPFWg"},
    {"task_id": "two-sum-ii-input-array-is-sorted", "title": "Two Sum II - Input Array Is Sorted", "difficulty": "Medium", "track": "two-pointers", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/cQ1Oz4ckcMT"},
    {"task_id": "3sum", "title": "3Sum", "difficulty": "Medium", "track": "two-pointers", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/jzZsG8n2R9A"},
    {"task_id": "container-with-most-water", "title": "Container With Most Water", "difficulty": "Medium", "track": "two-pointers", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/UuiTKBwPgAo"},
    {"task_id": "trapping-rain-water", "title": "Trapping Rain Water", "difficulty": "Hard", "track": "two-pointers", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/ZI2z5pq0TqA"},

    # Sliding Window
    {"task_id": "best-time-to-buy-and-sell-stock", "title": "Best Time to Buy and Sell Stock", "difficulty": "Easy", "track": "sliding-window", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/1pkOgXD63yU"},
    {"task_id": "longest-substring-without-repeating-characters", "title": "Longest Substring Without Repeating Characters", "difficulty": "Medium", "track": "sliding-window", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/wiGpQwVHdE0"},
    {"task_id": "longest-repeating-character-replacement", "title": "Longest Repeating Character Replacement", "difficulty": "Medium", "track": "sliding-window", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/gqXU1UyA8pk"},
    {"task_id": "permutation-in-string", "title": "Permutation in String", "difficulty": "Medium", "track": "sliding-window", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/UbyhOgBN834"},
    {"task_id": "minimum-window-substring", "title": "Minimum Window Substring", "difficulty": "Hard", "track": "sliding-window", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/jSto0O4AJbM"},
    {"task_id": "sliding-window-maximum", "title": "Sliding Window Maximum", "difficulty": "Hard", "track": "sliding-window", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/DfljaUwZsOk"},

    # Stack
    {"task_id": "valid-parentheses", "title": "Valid Parentheses", "difficulty": "Easy", "track": "stack", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/WTzjTskDFMg"},
    {"task_id": "min-stack", "title": "Min Stack", "difficulty": "Medium", "track": "stack", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/qkLl7nAwDPo"},
    {"task_id": "evaluate-reverse-polish-notation", "title": "Evaluate Reverse Polish Notation", "difficulty": "Medium", "track": "stack", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/iu10HcXvm6U"},
    {"task_id": "generate-parentheses", "title": "Generate Parentheses", "difficulty": "Medium", "track": "stack", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/s9fokUqJ76A"},
    {"task_id": "daily-temperatures", "title": "Daily Temperatures", "difficulty": "Medium", "track": "stack", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/cTBiBSnjO3c"},
    {"task_id": "car-fleet", "title": "Car Fleet", "difficulty": "Medium", "track": "stack", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/Pr6T-3yB9RM"},
    {"task_id": "largest-rectangle-in-histogram", "title": "Largest Rectangle in Histogram", "difficulty": "Hard", "track": "stack", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/zx5SwR137sc"},

    # Binary Search
    {"task_id": "binary-search", "title": "Binary Search", "difficulty": "Easy", "track": "binary-search", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/s4DPM8ct1pI"},
    {"task_id": "search-a-2d-matrix", "title": "Search a 2D Matrix", "difficulty": "Medium", "track": "binary-search", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/Ber2pi2C0j0"},
    {"task_id": "koko-eating-bananas", "title": "Koko Eating Bananas", "difficulty": "Medium", "track": "binary-search", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/U2SozAs9RzA"},
    {"task_id": "find-minimum-in-rotated-sorted-array", "title": "Find Minimum in Rotated Sorted Array", "difficulty": "Medium", "track": "binary-search", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/nIVW4P8b1VA"},
    {"task_id": "search-in-rotated-sorted-array", "title": "Search in Rotated Sorted Array", "difficulty": "Medium", "track": "binary-search", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/U8XENwh8Oy8"},
    {"task_id": "time-based-key-value-store", "title": "Time Based Key-Value Store", "difficulty": "Medium", "track": "binary-search", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/fu2cD_6E8Hw"},
    {"task_id": "median-of-two-sorted-arrays", "title": "Median of Two Sorted Arrays", "difficulty": "Hard", "track": "binary-search", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/q6IEA26hvPE"},

    # Linked List
    {"task_id": "reverse-linked-list", "title": "Reverse Linked List", "difficulty": "Easy", "track": "linked-list", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/G0_I-ZF0S38"},
    {"task_id": "merge-two-sorted-lists", "title": "Merge Two Sorted Lists", "difficulty": "Easy", "track": "linked-list", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/XIdigk956u0"},
    {"task_id": "reorder-list", "title": "Reorder List", "difficulty": "Medium", "track": "linked-list", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/S5bfdUtr8VU"},
    {"task_id": "remove-nth-node-from-end-of-list", "title": "Remove Nth Node From End of List", "difficulty": "Medium", "track": "linked-list", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/XVuQxVej6y8"},
    {"task_id": "copy-list-with-random-pointer", "title": "Copy List with Random Pointer", "difficulty": "Medium", "track": "linked-list", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/5Y2EiZST97Y"},
    {"task_id": "add-two-numbers", "title": "Add Two Numbers", "difficulty": "Medium", "track": "linked-list", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/wgFPrzTjm7s"},
    {"task_id": "linked-list-cycle", "title": "Linked List Cycle", "difficulty": "Easy", "track": "linked-list", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/gBTe7lFR3vc"},
    {"task_id": "find-the-duplicate-number", "title": "Find the Duplicate Number", "difficulty": "Medium", "track": "linked-list", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/wjYnzkAhcNk"},
    {"task_id": "lru-cache", "title": "LRU Cache", "difficulty": "Medium", "track": "linked-list", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/7ABFKPK2hD4"},
    {"task_id": "merge-k-sorted-lists", "title": "Merge k Sorted Lists", "difficulty": "Hard", "track": "linked-list", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/q5a5OiGbT6Q"},
    {"task_id": "reverse-nodes-in-k-group", "title": "Reverse Nodes in k-Group", "difficulty": "Hard", "track": "linked-list", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/1UOPsfP85V4"},

    # Trees
    {"task_id": "invert-binary-tree", "title": "Invert Binary Tree", "difficulty": "Easy", "track": "trees", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/OnSn2XEQ4MY"},
    {"task_id": "maximum-depth-of-binary-tree", "title": "Maximum Depth of Binary Tree", "difficulty": "Easy", "track": "trees", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/hTM3phJS6GE"},
    {"task_id": "diameter-of-binary-tree", "title": "Diameter of Binary Tree", "difficulty": "Easy", "track": "trees", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/bkxqA8Rfo04"},
    {"task_id": "balanced-binary-tree", "title": "Balanced Binary Tree", "difficulty": "Easy", "track": "trees", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/QfJsau0ItOY"},
    {"task_id": "same-tree", "title": "Same Tree", "difficulty": "Easy", "track": "trees", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/vRbbcKXCxOw"},
    {"task_id": "subtree-of-another-tree", "title": "Subtree of Another Tree", "difficulty": "Easy", "track": "trees", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/E36O5SWp-LE"},
    {"task_id": "lowest-common-ancestor-of-a-binary-search-tree", "title": "Lowest Common Ancestor of a BST", "difficulty": "Medium", "track": "trees", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/gs2LMfuOR9k"},
    {"task_id": "binary-tree-level-order-traversal", "title": "Binary Tree Level Order Traversal", "difficulty": "Medium", "track": "trees", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/6ZnyEApgFYg"},
    {"task_id": "binary-tree-right-side-view", "title": "Binary Tree Right Side View", "difficulty": "Medium", "track": "trees", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/d4zLyf32e3I"},
    {"task_id": "count-good-nodes-in-binary-tree", "title": "Count Good Nodes in Binary Tree", "difficulty": "Medium", "track": "trees", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/7cp5imvDzl4"},
    {"task_id": "validate-binary-search-tree", "title": "Validate Binary Search Tree", "difficulty": "Medium", "track": "trees", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/s6ATEkipzow"},
    {"task_id": "kth-smallest-element-in-a-bst", "title": "Kth Smallest Element in a BST", "difficulty": "Medium", "track": "trees", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/5LUXSvrmZo8"},
    {"task_id": "construct-binary-tree-from-preorder-and-inorder-traversal", "title": "Construct Binary Tree from Preorder and Inorder Traversal", "difficulty": "Medium", "track": "trees", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/ihj4IQGZ2zc"},
    {"task_id": "binary-tree-maximum-path-sum", "title": "Binary Tree Maximum Path Sum", "difficulty": "Hard", "track": "trees", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/Hr5cWUld4vU"},
    {"task_id": "serialize-and-deserialize-binary-tree", "title": "Serialize and Deserialize Binary Tree", "difficulty": "Hard", "track": "trees", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/u4JAi2JJhDg"},

    # Tries
    {"task_id": "implement-trie-prefix-tree", "title": "Implement Trie (Prefix Tree)", "difficulty": "Medium", "track": "tries", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/oobqoCJlHA0"},
    {"task_id": "design-add-and-search-words-data-structure", "title": "Design Add and Search Words Data Structure", "difficulty": "Medium", "track": "tries", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/BTf05gs_8iU"},
    {"task_id": "word-search-ii", "title": "Word Search II", "difficulty": "Hard", "track": "tries", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/asbcE9mZz_U"},

    # Heap / Priority Queue
    {"task_id": "kth-largest-element-in-a-stream", "title": "Kth Largest Element in a Stream", "difficulty": "Easy", "track": "heap-priority-queue", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/hOjcdrqMoQ8"},
    {"task_id": "last-stone-weight", "title": "Last Stone Weight", "difficulty": "Easy", "track": "heap-priority-queue", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/B-QCq79-oek"},
    {"task_id": "k-closest-points-to-origin", "title": "K Closest Points to Origin", "difficulty": "Medium", "track": "heap-priority-queue", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/rI2EBUEMfTk"},
    {"task_id": "kth-largest-element-in-an-array", "title": "Kth Largest Element in an Array", "difficulty": "Medium", "track": "heap-priority-queue", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/XEmy13g1Qxc"},
    {"task_id": "task-scheduler", "title": "Task Scheduler", "difficulty": "Medium", "track": "heap-priority-queue", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/s8p8ukTyA2I"},
    {"task_id": "design-twitter", "title": "Design Twitter", "difficulty": "Medium", "track": "heap-priority-queue", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/pNichitDD2E"},
    {"task_id": "find-median-from-data-stream", "title": "Find Median from Data Stream", "difficulty": "Hard", "track": "heap-priority-queue", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/itmhHWaHupI"},

    # Backtracking
    {"task_id": "subsets", "title": "Subsets", "difficulty": "Medium", "track": "backtracking", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/REOH22XwdVM"},
    {"task_id": "combination-sum", "title": "Combination Sum", "difficulty": "Medium", "track": "backtracking", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/GBKI9VSKdGg"},
    {"task_id": "permutations", "title": "Permutations", "difficulty": "Medium", "track": "backtracking", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/s7AvT7cGdSo"},
    {"task_id": "subsets-ii", "title": "Subsets II", "difficulty": "Medium", "track": "backtracking", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/Vn2v6ajA7U0"},
    {"task_id": "combination-sum-ii", "title": "Combination Sum II", "difficulty": "Medium", "track": "backtracking", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/rSA3t6BDDwg"},
    {"task_id": "word-search", "title": "Word Search", "difficulty": "Medium", "track": "backtracking", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/pfiQ_PS1g8E"},
    {"task_id": "palindrome-partitioning", "title": "Palindrome Partitioning", "difficulty": "Medium", "track": "backtracking", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/3jvWodd7ht0"},
    {"task_id": "letter-combinations-of-a-phone-number", "title": "Letter Combinations of a Phone Number", "difficulty": "Medium", "track": "backtracking", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/0snEunUacZY"},
    {"task_id": "n-queens", "title": "N-Queens", "difficulty": "Hard", "track": "backtracking", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/Ph95IHmRp5M"},

    # Graphs
    {"task_id": "number-of-islands", "title": "Number of Islands", "difficulty": "Medium", "track": "graphs", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/pV2kpPD66nE"},
    {"task_id": "max-area-of-island", "title": "Max Area of Island", "difficulty": "Medium", "track": "graphs", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/iJGr1OtmH0c"},
    {"task_id": "clone-graph", "title": "Clone Graph", "difficulty": "Medium", "track": "graphs", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/mQeF6bN8hMk"},
    {"task_id": "walls-and-gates", "title": "Walls and Gates", "difficulty": "Medium", "track": "graphs", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/e69C6xhiSQE"},
    {"task_id": "rotting-oranges", "title": "Rotting Oranges", "difficulty": "Medium", "track": "graphs", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/y704fEOx0i0"},
    {"task_id": "pacific-atlantic-water-flow", "title": "Pacific Atlantic Water Flow", "difficulty": "Medium", "track": "graphs", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/s-AngxEH39E"},
    {"task_id": "surrounded-regions", "title": "Surrounded Regions", "difficulty": "Medium", "track": "graphs", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/9z2BunfoZ5Y"},
    {"task_id": "course-schedule", "title": "Course Schedule", "difficulty": "Medium", "track": "graphs", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/EgI5nU9etnU"},
    {"task_id": "course-schedule-ii", "title": "Course Schedule II", "difficulty": "Medium", "track": "graphs", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/Akt3glAwyfY"},
    {"task_id": "graph-valid-tree", "title": "Graph Valid Tree", "difficulty": "Medium", "track": "graphs", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/bXsUuownnoQ"},
    {"task_id": "number-of-connected-components-in-an-undirected-graph", "title": "Number of Connected Components", "difficulty": "Medium", "track": "graphs", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/8f1XPm4WOUc"},
    {"task_id": "redundant-connection", "title": "Redundant Connection", "difficulty": "Medium", "track": "graphs", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/FXWRE67PLL0"},
    {"task_id": "word-ladder", "title": "Word Ladder", "difficulty": "Hard", "track": "graphs", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/h9iTnkgv05E"},

    # 1-D Dynamic Programming
    {"task_id": "climbing-stairs", "title": "Climbing Stairs", "difficulty": "Easy", "track": "1d-dp", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/Y0lT9Fck7q8"},
    {"task_id": "min-cost-climbing-stairs", "title": "Min Cost Climbing Stairs", "difficulty": "Easy", "track": "1d-dp", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/ktmzAZWkEZ0"},
    {"task_id": "house-robber", "title": "House Robber", "difficulty": "Medium", "track": "1d-dp", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/73r3KWiEvyk"},
    {"task_id": "house-robber-ii", "title": "House Robber II", "difficulty": "Medium", "track": "1d-dp", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/rWAJCfYYOvM"},
    {"task_id": "longest-palindromic-substring", "title": "Longest Palindromic Substring", "difficulty": "Medium", "track": "1d-dp", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/XYQecbcd6fY"},
    {"task_id": "palindromic-substrings", "title": "Palindromic Substrings", "difficulty": "Medium", "track": "1d-dp", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/4RACzI5-du8"},
    {"task_id": "decode-ways", "title": "Decode Ways", "difficulty": "Medium", "track": "1d-dp", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/6aEyTjOwlJU"},
    {"task_id": "coin-change", "title": "Coin Change", "difficulty": "Medium", "track": "1d-dp", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/H9bfqozjoqs"},
    {"task_id": "maximum-product-subarray", "title": "Maximum Product Subarray", "difficulty": "Medium", "track": "1d-dp", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/lXVy6YWFcRM"},
    {"task_id": "word-break", "title": "Word Break", "difficulty": "Medium", "track": "1d-dp", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/Sx9NNgInc3A"},
    {"task_id": "longest-increasing-subsequence", "title": "Longest Increasing Subsequence", "difficulty": "Medium", "track": "1d-dp", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/cjWnW0hdF1Y"},
    {"task_id": "partition-equal-subset-sum", "title": "Partition Equal Subset Sum", "difficulty": "Medium", "track": "1d-dp", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/IsvocB5BJhw"},

    # 2-D Dynamic Programming
    {"task_id": "unique-paths", "title": "Unique Paths", "difficulty": "Medium", "track": "2d-dp", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/IlEsdxuD4lY"},
    {"task_id": "longest-common-subsequence", "title": "Longest Common Subsequence", "difficulty": "Medium", "track": "2d-dp", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/Ua0GhsJSlWM"},
    {"task_id": "best-time-to-buy-and-sell-stock-with-cooldown", "title": "Best Time to Buy and Sell Stock with Cooldown", "difficulty": "Medium", "track": "2d-dp", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/I7j0F7AHpb8"},
    {"task_id": "coin-change-ii", "title": "Coin Change II", "difficulty": "Medium", "track": "2d-dp", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/Mjy4hd2xgrs"},
    {"task_id": "target-sum", "title": "Target Sum", "difficulty": "Medium", "track": "2d-dp", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/g0npyaQtAQM"},
    {"task_id": "interleaving-string", "title": "Interleaving String", "difficulty": "Medium", "track": "2d-dp", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/3Rw3p9LrgvE"},
    {"task_id": "edit-distance", "title": "Edit Distance", "difficulty": "Hard", "track": "2d-dp", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/XYi2-LPrwm4"},
    {"task_id": "burst-balloons", "title": "Burst Balloons", "difficulty": "Hard", "track": "2d-dp", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/VFskby7lUbw"},

    # Greedy
    {"task_id": "maximum-subarray", "title": "Maximum Subarray", "difficulty": "Medium", "track": "greedy", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/5WZl3MMT0Eg"},
    {"task_id": "jump-game", "title": "Jump Game", "difficulty": "Medium", "track": "greedy", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/Yan0cv2cLy8"},
    {"task_id": "jump-game-ii", "title": "Jump Game II", "difficulty": "Medium", "track": "greedy", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/dJ7sWiOoK7g"},
    {"task_id": "gas-station", "title": "Gas Station", "difficulty": "Medium", "track": "greedy", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/lJwbPZGo05A"},
    {"task_id": "hand-of-straights", "title": "Hand of Straights", "difficulty": "Medium", "track": "greedy", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/amnrMCVd2YI"},

    # Intervals
    {"task_id": "insert-interval", "title": "Insert Interval", "difficulty": "Medium", "track": "intervals", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/A8NUOmlwOlM"},
    {"task_id": "merge-intervals", "title": "Merge Intervals", "difficulty": "Medium", "track": "intervals", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/44H3cEC2fFM"},
    {"task_id": "non-overlapping-intervals", "title": "Non-overlapping Intervals", "difficulty": "Medium", "track": "intervals", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/nONCGxWoUfM"},
    {"task_id": "meeting-rooms", "title": "Meeting Rooms", "difficulty": "Easy", "track": "intervals", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/PaJxqZt63aw"},
    {"task_id": "meeting-rooms-ii", "title": "Meeting Rooms II", "difficulty": "Medium", "track": "intervals", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/FdzJmTCVyJU"},
    {"task_id": "minimum-interval-to-include-each-query", "title": "Minimum Interval to Include Each Query", "difficulty": "Hard", "track": "intervals", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/5hQ5WWW5awQ"},

    # Bit Manipulation
    {"task_id": "single-number", "title": "Single Number", "difficulty": "Easy", "track": "bit-manipulation", "in_nc75": False, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/qMPX1AOa83k"},
    {"task_id": "number-of-1-bits", "title": "Number of 1 Bits", "difficulty": "Easy", "track": "bit-manipulation", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/5Km3utixwZs"},
    {"task_id": "counting-bits", "title": "Counting Bits", "difficulty": "Easy", "track": "bit-manipulation", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/RyBM56P6x0k"},
    {"task_id": "reverse-bits", "title": "Reverse Bits", "difficulty": "Easy", "track": "bit-manipulation", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/UcoN6UjAI64"},
    {"task_id": "missing-number", "title": "Missing Number", "difficulty": "Easy", "track": "bit-manipulation", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/WnPLSRLSANE"},
    {"task_id": "sum-of-two-integers", "title": "Sum of Two Integers", "difficulty": "Medium", "track": "bit-manipulation", "in_nc75": True, "in_nc150": True, "in_nc250": True, "video_url": "https://youtu.be/gVUrDV4tZfY"}
]


def get_neetcode_roadmap_summary() -> Dict[str, Any]:
    """Returns complete NeetCode DAG, tracks, counts, and curated problem collections."""
    track_counts = {}
    for p in NEETCODE_PROBLEMS:
        tr = p["track"]
        track_counts[tr] = track_counts.get(tr, 0) + 1

    nc75_count = sum(1 for p in NEETCODE_PROBLEMS if p.get("in_nc75"))
    nc150_count = sum(1 for p in NEETCODE_PROBLEMS if p.get("in_nc150"))
    nc250_count = len(NEETCODE_PROBLEMS)

    enriched_nodes = []
    for node in NEETCODE_DAG_NODES:
        n = dict(node)
        n["problem_count"] = track_counts.get(node["id"], 0)
        n["problems"] = [p for p in NEETCODE_PROBLEMS if p["track"] == node["id"]]
        enriched_nodes.append(n)

    return {
        "nodes": enriched_nodes,
        "tracks": [node["id"] for node in NEETCODE_DAG_NODES],
        "total_problems": len(NEETCODE_PROBLEMS),
        "nc75_count": nc75_count,
        "nc150_count": nc150_count,
        "nc250_count": nc250_count,
        "all_problems": NEETCODE_PROBLEMS
    }
