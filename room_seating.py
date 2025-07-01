import csv
from seating_algorithm import (
    assign_seating_single_row_modified,
    assign_seating_by_group_multirow,
)

def read_rooms_csv(filename):
    """
    Reads the CSV file containing room data and returns a list of room dictionaries.
    Each room has: 'اسم القاعة' (name), 'عدد الكراسي' (total seats), and 'عدد الصفوف' (number of rows).
    """
    rooms = []
    with open(filename, encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rooms.append({
                "اسم القاعة": row["اسم القاعة"],
                "عدد الكراسي": int(row["عدد الكراسي"]),
                "عدد الصفوف": int(row["عدد الصفوف"]),
            })
    return rooms

def main():
    # Read room information from CSV.
    rooms = read_rooms_csv("القاعات والكراسي التحديث الاخير.csv")
    print("Available Rooms:")
    for idx, room in enumerate(rooms):
        print(f"{idx+1}. {room['اسم القاعة']} - Total Seats: {room['عدد الكراسي']}, Rows: {room['عدد الصفوف']}")

    # Allow the user to select a room.
    choice = input("Enter the number of the room you want to select: ")
    try:
        choice_idx = int(choice) - 1
        if choice_idx < 0 or choice_idx >= len(rooms):
            print("Invalid selection. Exiting.")
            return
    except ValueError:
        print("Invalid input. Exiting.")
        return

    selected_room = rooms[choice_idx]
    total_seats = selected_room["عدد الكراسي"]
    row_count = selected_room["عدد الصفوف"]

    print(f"\nYou selected '{selected_room['اسم القاعة']}' with {total_seats} seats and {row_count} row(s).")

    # For demonstration: define sample attendees spanning all ranks.
    # In the final system, this selection comes from user input.
    sample_attendees = [
        {'name': 'الملك', 'rank': 1, 'selection_order': 1},
        {'name': 'ولي العهد', 'rank': 2, 'selection_order': 2},
    ]
    # Add sample data for groups.
    for i in range(18):
        sample_attendees.append({'name': f'أصحاب السمو {i+1}', 'rank': 3, 'selection_order': 3+i})
    for i in range(5):
        sample_attendees.append({'name': f'أصحاب المعالي {i+1}', 'rank': 4, 'selection_order': 21+i})
    for i in range(3):
        sample_attendees.append({'name': f'أصحاب الفضيلة {i+1}', 'rank': 5, 'selection_order': 26+i})
    for i in range(2):
        sample_attendees.append({'name': f'أصحاب السعادة {i+1}', 'rank': 6, 'selection_order': 29+i})
    for i in range(2):
        sample_attendees.append({'name': f'شيوخ القبائل {i+1}', 'rank': 7, 'selection_order': 31+i})

    print("\nAssigning seats using sample attendee data...\n")
    if row_count == 1:
        seating_arrangement = assign_seating_single_row_modified(sample_attendees, total_seats)
        print("Seating Arrangement (Single Row):")
        for idx, seat in enumerate(seating_arrangement):
            if seat:
                print(f"Seat {idx+1}: {seat['name']} (Rank: {seat['rank']})")
            else:
                print(f"Seat {idx+1}: Empty")
    else:
        seating = assign_seating_by_group_multirow(sample_attendees, total_seats, row_count)
        print("Seating Arrangement (Multi-Row):")
        for row_idx, row in enumerate(seating):
            print(f"Row {row_idx+1}: " + " | ".join(
                f"{seat['name']} (Rank {seat['rank']})" if seat else "Empty" for seat in row
            ))

if __name__ == "__main__":
    main()
