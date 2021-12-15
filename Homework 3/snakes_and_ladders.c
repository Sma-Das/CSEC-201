#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <time.h>

#define SIZE 10


// Constants
static const char LADDER = 'L';
static const char SNAKE = 'S';
static const char PLAYER = 'P';

// Snakes and Ladders board
int (*board)[SIZE];

// Testing purposes to check the board
void print_board(void);

// Function prototypes
int random_num(int limit);
void insert_piece(int amount, char pieces);
int get_move(void);
void move_player(int steps, int *curr_pos, bool replace);

int main(void)
{
    // Allocate space for the board and init to 0
    board = calloc(SIZE * SIZE, sizeof(int));

    if (board == NULL)
    {
        printf("Could not allocate space for the board!");
        return 1;
    }

    // Seed random number
    srand(time(NULL));

    // add 5 snakes to the board
    insert_piece(5, SNAKE);

    // add 5 ladders to the board
    insert_piece(5, LADDER);

    // positional pointers for player position
    int *curr_pos = calloc(1, sizeof(int));

    if (curr_pos == NULL)
    {
        printf("Could not allocate space for the player!");
        return 2;
    }

    // Main game loop
    while (board[SIZE - 1][SIZE - 1] != PLAYER)
    {
        printf("Currently at position [%i]\n", *curr_pos);
        int steps = get_move();

        move_player(steps, curr_pos, true);
    }

    // Validate win
    if (board[SIZE - 1][SIZE - 1] == PLAYER && *curr_pos == 99)
    {
        printf("You won! Congrats!");
    }
    else
    {
        printf("Could not register win, invalid board position");
    }

// Exiting the program
quit:
    free(board);
    free(curr_pos);
    return 0;
}

// Print the board - mainly for testing purposes
void print_board(void)
{
    for (int i = 0; i < SIZE; ++i)
    {
        for (int j = 0; j < SIZE; ++j)
        {
            if (board[i][j] == 0)
            {
                printf(" ");
            }
            else
            {
                printf("%c", board[i][j]);
            }
            printf(" | ");
        }
        printf("\n");
    }
    return;
}

// Generate a proper random number - not a somewhat random number
int random_num(int limit)
{
    int divisor = RAND_MAX / (limit + 1);
    int retval;

    do
    {
        retval = rand() / divisor;
    } while (retval > limit);

    return retval;
}

// Insert pieces onto the board
void insert_piece(int amount, char pieces)
{
    /* 
    Potential to override an existing piece but I like it that way
    Up to their fortune/misfortune
    */

    for (int i = 0; i < amount; ++i)
    {
        // Random amount of steps between 94 and 5
        int position = random_num(94 - 5) + 5;
        board[position % SIZE][position / SIZE] = pieces;
    }
    return;
}

// Get a valid integer between 0 - 6 from the player
int get_move(void)
{
    int steps;
    char line[256];
    do
    {
        printf("Enter a dice number between 1 - 6: ");
        fgets(line, sizeof(line), stdin);
        // Check for invalid input
        if (!sscanf(line, "%i", &steps))
        {
            continue;
        }
    } while (steps < 1 || steps > 6);

    return steps;
}

// Move the player a set amount of steps accounting for potential objects
void move_player(int steps, int *curr_pos, bool replace)
{
    int new_pos = *curr_pos + steps;
    if (new_pos < 0)
    {
        new_pos = 0;
    }
    else if (new_pos > 99)
    {
        new_pos = 99;
    }

    int new_row = new_pos / SIZE, curr_row = (new_pos - steps) / SIZE;
    int new_col = new_pos % SIZE, curr_col = (new_pos - steps) % SIZE;

    int new_location = board[new_row][new_col];

    // Replace the player's piece if needed
    if (replace)
    {
        board[curr_row][curr_col] = 0;
    }
    *curr_pos = new_pos;

    if (new_location != 0)
    {
        int random_steps = random_num(94 - 5) + 5;
        if (new_location == SNAKE)
        {
            printf("Oh no! A snake!\n");
            move_player(-1 * random_steps, curr_pos, false);
        }
        else if (new_location == LADDER)
        {
            printf("Lucky you! A ladder!\n");
            move_player(random_steps, curr_pos, false);
        }
        else
        {
            printf("Unknown piece at position [%i] -> [%c]\n", *curr_pos, new_location);
        }
        printf("That was %i positions!\n", random_steps);
    }
    else
    {
        board[new_row][new_col] = PLAYER;
    }
    return;
}
