
import pygame
import os
# Constants
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 200
SQUARE_SIZE = 7
SQUARE_SPACING = 5
TEXT_PADDING = 100  # Space for "Batches:" text
# TOTAL_BATCHES = 10  # Total number of squares
COMPLETED_BATCHES = 6  # Change this to test different completed batch counts


def count_non_blank_lines(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        non_blank_lines = [line for line in file if line.strip()]  # Filter out blank lines
    return len(non_blank_lines)


def draw_stats(num_batches, num_runs_per_batch, output_dir, x, y):
    file_path = f"{output_dir}/output_data.txt"
    non_blank_count = count_non_blank_lines(file_path)
    # print(f"Number of non-blank lines: {non_blank_count}")

    completed_batches, completed_runs = divmod(non_blank_count, num_runs_per_batch)
    runs_in_progress = num_runs_per_batch - completed_runs

    # print(f"Total non-blank lines: {non_blank_count}")
    # print(f"Completed batches: {completed_batches}")
    # print(f"Runs remaining: {runs_in_progress}")
    # Render "Batches:" text
    text_surface = font.render("Batches:", True, BLACK)
    screen.blit(text_surface, (x, y))
    text_surface = font.render("Sims In progress:", True, BLACK)
    screen.blit(text_surface, (x, y + 20))

    # Draw batch squares
    for i in range(num_batches):
        color = RED if i < completed_batches else GREEN
        x_pos = x + i * (SQUARE_SIZE + SQUARE_SPACING) + 150
        y_pos = y + SQUARE_SIZE//2
        pygame.draw.rect(screen, color, (x_pos, y_pos, SQUARE_SIZE, SQUARE_SIZE))
    # Draw runs in progress squares
    for i in range(num_runs_per_batch):
        color = RED if i < completed_runs else GREEN
        x_pos = x + i * (SQUARE_SIZE + SQUARE_SPACING) + 150
        y_pos = y + SQUARE_SIZE//2 + 20
        pygame.draw.rect(screen, color, (x_pos, y_pos, SQUARE_SIZE, SQUARE_SIZE))

output_dir = ""
output_dir_base = "out/2025_03_24_21_26_00"
if os.path.exists(f"{output_dir_base}/TRAIN_OPTIMIZATION"):
    output_dir = f"{output_dir_base}/TRAIN_OPTIMIZATION"
elif os.path.exists(f"{output_dir_base}/TRAIN_BLUETOOTH"):
    output_dir = f"{output_dir_base}/TRAIN_BLUETOOTH"

num_batches = 5
num_runs_per_batch = 10
X = 10
Y = SCREEN_HEIGHT // 2 - 10

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Batch Progress")
font = pygame.font.Font(None, 24)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

# Main loop
running = True
while running:
    screen.fill(WHITE)  # Background color

    draw_stats(num_batches, num_runs_per_batch, output_dir, X, Y)

    pygame.display.flip()  # Update screen

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
