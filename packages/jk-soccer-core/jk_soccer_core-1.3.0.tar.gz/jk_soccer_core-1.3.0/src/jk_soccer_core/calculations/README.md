# Calculations

## RPI Calculations

### Element 1: Teams Winning Percentage

Element 1 of the RPI compares the number of games Team A has won and tied to the total games Team A has played.
For purposes if this Element, the formula treats a tie as half a win and half a loss.  The formula is as follows:

```plaintext
(W+1/2T)/((W+1/2T)+(L+1/2T))
```

which simplifies to:

```plaintext
(W+1/2T)/(W+L+T)
```

In this formula, W is Team A's wins; T is Team A's ties; and L is Team A's losses.
**Games determined by penalty kicks are considered ties.**

So, if Team A has a record of 8 wins, 8 losses, and 4 ties, Element 1 of it's RPI is:

```plaintext
(8+1/2*4)/(8+8+4) = 10/20 = 0.500
```

Element 1 tells only Team A's wins and teis compared to it's games played.  It tells nothing about the strength
of Team A's opponents.

Interestingly, the RPI's valuation of a tie has half a win and half a loss is different than how conferences 
treat ties for conference standing purposes.  Conferences treat a win as worth 3 points and a tie as worth 1.  
The 3:1 ratio is how soccer leagues worldwide almost universally compute standings.

### Element 2: Opponents' Average Winning Percentage (Against Other Teams)

Element 2 measures a team's opponents' average winning percentage **(against teams other than Team A)**.  
The NCAA's stated purpose of Element 2, combined with Element 3, is to measure the **strength of schedule** against
which Team A achieved it's Element 1 Winning Percentage.

To determine Team A's opponents average winning percentage, the NCAA first computes, for each of Team A's opponents,
the opponent's wins and ties that as compared to the opponent's total games played, in the same way it does the 
calculation for Team A's Element 1. The only difference is that the NCAA excludes the opponent's games against Team A
itself. Thus the first part of the computation determines each opponent's Element 1 based on games played against teams
other than Team A.