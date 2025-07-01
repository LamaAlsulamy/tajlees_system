#############################################
# seating_algorithm.py
#############################################

def assign_seating_single_row_modified(selected_attendees, total_seats):
    """
    Modified seating assignment for a single row (e.g. 31 chairs) with the following rules:
      • The highest-ranked attendee (King, rank 1) is placed in the center.
      • The Crown Prince (rank 2) is placed immediately to the right of the center.
      • Group3 ("أصحاب السمو", rank 3) fills the right side first; any overflow goes on the left (closest to the King).
      • Group4 ("أصحاب المعالي", rank 4) is then placed on the left side (using remaining seats closest to the King). 
      • Remaining groups (ranks 5, 6, 7) are merged (keeping their selection order) and fill the leftover seats, preferred by proximity to the center.
    """
    seating = [None] * total_seats
    center = total_seats // 2  # For example, with 31 seats, center index is 15 (0-indexed 0..30)

    # Separate attendees by rank.
    kings = [p for p in selected_attendees if p['rank'] == 1]
    crown_princes = [p for p in selected_attendees if p['rank'] == 2]
    group3 = sorted([p for p in selected_attendees if p['rank'] == 3], key=lambda x: x['selection_order'])
    group4 = sorted([p for p in selected_attendees if p['rank'] == 4], key=lambda x: x['selection_order'])
    group5 = sorted([p for p in selected_attendees if p['rank'] == 5], key=lambda x: x['selection_order'])
    group6 = sorted([p for p in selected_attendees if p['rank'] == 6], key=lambda x: x['selection_order'])
    group7 = sorted([p for p in selected_attendees if p['rank'] == 7], key=lambda x: x['selection_order'])

    # Place the King in the center.
    if kings:
        seating[center] = kings[0]
    else:
        seating[center] = selected_attendees[0]

    # Place the Crown Prince immediately to the right.
    right_index = center + 1
    if crown_princes:
        seating[right_index] = crown_princes[0]
        right_index += 1

    # Define available seat indices on each side.
    right_seats = list(range(right_index, total_seats))
    left_seats = list(range(center - 1, -1, -1))

    # ------------------- Place Group 3 ("أصحاب السمو") -------------------
    overflow_group3 = []
    if len(group3) <= len(right_seats):
        for idx, person in enumerate(group3):
            seating[right_seats[idx]] = person
    else:
        for idx, person in enumerate(group3[:len(right_seats)]):
            seating[right_seats[idx]] = person
        overflow_group3 = group3[len(right_seats):]

    # Place any overflow from group 3 on the left.
    if overflow_group3:
        if len(overflow_group3) <= len(left_seats):
            for idx, person in enumerate(overflow_group3):
                seating[left_seats[idx]] = person
            left_seats = left_seats[len(overflow_group3):]
        else:
            for idx, person in enumerate(overflow_group3[:len(left_seats)]):
                seating[left_seats[idx]] = person
            left_seats = []

    # ------------------- Place Group 4 ("أصحاب المعالي") -------------------
    overflow_group4 = []
    if len(group4) <= len(left_seats):
        for idx, person in enumerate(group4):
            seating[left_seats[idx]] = person
    else:
        for idx, person in enumerate(group4[:len(left_seats)]):
            seating[left_seats[idx]] = person
        overflow_group4 = group4[len(left_seats):]
        remaining_right = [r for r in right_seats if seating[r] is None]
        if overflow_group4:
            if len(overflow_group4) <= len(remaining_right):
                for idx, person in enumerate(overflow_group4):
                    seating[remaining_right[idx]] = person
            else:
                for idx, person in enumerate(overflow_group4[:len(remaining_right)]):
                    seating[remaining_right[idx]] = person

    # ------------------- Place Remaining Groups (Ranks 5, 6 & 7) -------------------
    others = group5 + group6 + group7
    remaining_indices = [i for i, seat in enumerate(seating) if seat is None]
    remaining_indices.sort(key=lambda i: abs(i - center))
    for idx, person in enumerate(others):
        if idx < len(remaining_indices):
            seating[remaining_indices[idx]] = person

    return seating

# ------------------- Multi-Row Seating Algorithm -------------------
def find_contiguous_block_in_region(row, block_size, left_bound, right_bound):
    """
    In a given row (list), find a contiguous block of empty seats (None)
    between left_bound and right_bound (inclusive) that fits block_size people.
    Returns the starting index if found; otherwise, returns None.
    """
    count = 0
    start_index = None
    for i in range(left_bound, right_bound + 1):
        if row[i] is None:
            if start_index is None:
                start_index = i
            count += 1
            if count >= block_size:
                return start_index
        else:
            count = 0
            start_index = None
    return None

def assign_seating_by_group_multirow(selected_attendees, total_seats, row_count):
    """
    Seating assignment for rooms with multiple rows.
    Total seats are divided evenly among rows. The highest-ranked person is placed in the center of row 0.
    Then each rank group (using our grouping logic from the single-row function) is placed as a contiguous
    block in a row. The preferred region for rank 3 is to the right of center;
    for rank 4, to the left; and others default to left.
    If a contiguous block isn’t found in one row, subsequent rows are scanned.
    """
    seats_per_row = total_seats // row_count
    seating = [[None] * seats_per_row for _ in range(row_count)]
    center = seats_per_row // 2

    sorted_attendees = sorted(selected_attendees, key=lambda x: (x['rank'], x['selection_order']))
    seating[0][center] = sorted_attendees[0]
    remaining_attendees = sorted_attendees[1:]

    groups = {}
    for attendee in remaining_attendees:
        groups.setdefault(attendee['rank'], []).append(attendee)
    for group in groups.values():
        group.sort(key=lambda x: x['selection_order'])

    def get_boundaries(row_index, preferred_side, group_size):
        if row_index == 0:
            if preferred_side == "left":
                return (0, center - 1)
            else:
                return (center + 1, seats_per_row - 1)
        else:
            if group_size <= (seats_per_row // 2):
                mid = seats_per_row // 2
                return (0, mid - 1) if preferred_side == "left" else (seats_per_row - (seats_per_row // 2), seats_per_row - 1)
            else:
                return (0, seats_per_row - 1)

    def try_place_group_in_row(row_idx, group, preferred_side):
        left_bound, right_bound = get_boundaries(row_idx, preferred_side, len(group))
        start_index = find_contiguous_block_in_region(seating[row_idx], len(group), left_bound, right_bound)
        if start_index is not None:
            for i, attendee in enumerate(group):
                seating[row_idx][start_index + i] = attendee
            return True
        return False

    for rank in sorted(groups.keys()):
        group = groups[rank]
        preferred_side = "right" if rank == 3 else ("left" if rank == 4 else "left")
        placed = False
        for row_idx in range(row_count):
            if try_place_group_in_row(row_idx, group, preferred_side):
                placed = True
                break
        if not placed:
            opposite_side = "right" if preferred_side == "left" else "left"
            for row_idx in range(row_count):
                if try_place_group_in_row(row_idx, group, opposite_side):
                    placed = True
                    break
            if not placed:
                print(f"Warning: Could not place group of rank {rank} with {len(group)} members as a contiguous block.")
    return seating

#############################################
# Testing Block: Run if executed directly.
#############################################
if __name__ == "__main__":
    # Single-row test (for 31 seats)
    total_seats = 31
    test_attendees = [
        {'name': 'الملك', 'rank': 1, 'selection_order': 1},
        {'name': 'ولي العهد', 'rank': 2, 'selection_order': 2},
    ]
    for i in range(18):
        test_attendees.append({'name': f'أصحاب السمو {i+1}', 'rank': 3, 'selection_order': 3+i})
    for i in range(5):
        test_attendees.append({'name': f'أصحاب المعالي {i+1}', 'rank': 4, 'selection_order': 21+i})
    for i in range(3):
        test_attendees.append({'name': f'أصحاب الفضيلة {i+1}', 'rank': 5, 'selection_order': 26+i})
    for i in range(2):
        test_attendees.append({'name': f'أصحاب السعادة {i+1}', 'rank': 6, 'selection_order': 29+i})
    for i in range(2):
        test_attendees.append({'name': f'شيوخ القبائل {i+1}', 'rank': 7, 'selection_order': 31+i})

    print("\n--- Single-Row Seating Arrangement ---")
    seating_arr = assign_seating_single_row_modified(test_attendees, total_seats)
    for idx, seat in enumerate(seating_arr):
        if seat:
            print(f"Seat {idx+1}: {seat['name']} (Rank: {seat['rank']})")
        else:
            print(f"Seat {idx+1}: Empty")

    # Multi-row test (for a room with 62 seats, 2 rows)
    total_seats_multi = 62
    row_count = 2
    print("\n--- Multi-Row Seating Arrangement ---")
    seating_multi = assign_seating_by_group_multirow(test_attendees, total_seats_multi, row_count)
    for row_idx, row in enumerate(seating_multi):
        print(f"Row {row_idx+1}: " + " | ".join(
            f"{seat['name']} (R{seat['rank']})" if seat else "Empty" for seat in row
        ))
