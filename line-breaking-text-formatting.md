# On the Line Breaking Problem in Text Formatting

James O. Achugbue<br/>
Department of Mathematical and Computer Sciences<br/>
Michigan Technological University, Houghton MI<br/>

ACM SIGPLAN Notices April 1981
https://doi.org/10.1145/872730.806462

## License

Permission to copy without fee all or part of this material is granted
provided that the copies are not made or distributed for direct
commercial advantage, the ACM copyright notice and the title of the
publication and its date appear, and notice is given that copying is
by permission of the Association for Computing Machinery. To copy
otherwise, or to republish, requires a fee and/or specific permission.

## ABSTRACT

A basic problem in text formatting is that of determining the break
points for separating a string of words into lines to obtain a
formatted paragraph. When formatted text is required to be aligned
with both the left and right margins, the choice of break points
greatly affects the quality of the formatted document. This paper
presents and discusses solutions to the line breaking problem. These
include the usual line-by-line method, a dynamic programming approach,
and a new algorithm which is optimal and runs almost as fast as the
line-by-line method.

## KEYWORDS

Text Formatting, line breaking, text alignment, computer typesetting,
dynamic programming.

## 1. INTRODUCTION

In this paper, we are concerned primarily with the design of
algorithms to format the text of a paragraph for printing on an output
device with fixed character positions, such as a line-printer. This is
to be contrasted with printing on output devices with arbitrary
character positions, such as graphic terminals and typesetting
equipment. The former is usually referred to as text formatting while
the term typesetting is applied to the latter type. Typesetting is the
main concern of systems such as [^3][^4][^5][^6]. While this unquestionably
yields documents of professional quality, the equipment required is
nevertheless unavailable to the majority of potential users. Thus, any
features which aim at improving the quality of text-formatting are most
welcome. A useful feature, often supplied by designers of text
formatting software, for example [^7][^8][^9], is the ability to align or
justify the formatted text with both left and right margins. Text
alignment poses two main problems. First, the determination of the
break points for separating the words of a paragraph into lines, and
second, the distribution of the surplus spaces on each line in between
the words of that line.

The first problem is usually solved by filling up each line as much as
possible and then proceeding to the next. This method will be
reviewed in the next section and used as a basis for the subsequent
development. While it is simple to implement and works well in many
situations, it does not always produce the best results when text is
being justified.

A common strategy for dealing with the second problem is to distribute
the surplus spaces for each line between the words starting
alternately from the left and right margins. Thus, if line one has
additional spaces, then the spaces between the first and second words,
the second and third words and so on will be increased by one until
the surplus spaces are used up. If line two also has surplus spaces,
it is now used up by increasing spaces between the last and the last
but one words, the last but one and the preceding word, and so on. The
aim of this strategy is to avoid "rivers" of white space running down
the length of the page. Another possibility would be to assign the
extra spaces to the inter-word gaps in a pseudo-random
manner. However, irrespective of the surplus space distribution
strategy, a poor line breaking algorithm will undoubtedly frequently
produce poorly formatted text. This paper therefore focuses
attentions on the line breaking problem.

Another important factor which should be taken into consideration in
connection with this problem is that of hyphenation. No doubt, a good
hyphenation algorithm will help improve the quality of formatted
text. However, hyphenation in itself is a complex problem and will be
left out for most of this presentation.

In sections 2 to 4 the algorithms are presented for
formatting. Section 5 discusses extensions to typesetting and
hpyenations.

## 2. THE LINE-BY-LINE METHOD

It is assumed that we have as input a paragraph consisting of a
sequence of N>0 words. Here, a words is simply a string of non-blank
characters. The number of characters in each word is given in the
array W[I], I <= I<=N. The paragraph will be formatted into M lines of
D charactesr each. The line breaking problem is solved by specifying
for the J-th line, 1<=J=M, the index S[J] of the first word of the
line. (The major variables used by all the algorithms are summarized
in table 1.)

<table>
<caption>Table 1: Major variables referenced by the algorithm</caption>
<tr><td>N</td><td>number of words in paragraph</td></tr>
<tr><td>M         </td><td> number of formatted lines</td></tr>
<tr><td>W[I]      </td><td> maxium number of characters per line</td></tr>
<tr><td>S[I]      </td><td> index of first word in I-th line, that is I-th line starts with W[S[I]].</td></tr>
<tr><td>L[I]      </td><td> length of I-th formatted line before distribution of surplus spaces.</td></tr>
<tr><td>E[I]      </td><td> index of first word, line I, for earliest breaking</td></tr>
<tr><td>F[K,J]    </td><td> formatted length from I-th to J-th word</td></tr>
<tr><td>C[I,J]    </td><td> cost function, dynamic programming</td></tr>
<tr><td>c[I]      </td><td> cost function, line-breaker, = C[I,N]</td></tr>
</table>

The line-by-line method is the one that immediately comes to mind and
has been used in many text formatting programs. It is strongly
appealing in its simplicity. THe computation of the break points of
equivalently the indices for words at the beginning of each line is
given in algorithm LINE-BY-LINE. Note that arrays L, S and W need not
be saved in actual implementations unless they are required for some
othe rpurposes. They are kept in this presentation to facilitate the
discussion in subsequent sections. Clearly, then, theline-by-line
method can be implemented so that it has O(N) worst case time
complexity and requires storage mainly for the one line of
output. (The algorithms are also given in a PASCAL-like fashion in the
appendix).

### ALGORITHM LINE-BY-LINE


```
---------------------------------------------
    /D,L,M,N,S,W are as given in Table 1/
(1) /initialize/
    M <- 1, S[1 <- 1, L[M] <- W[I]
    I <- 2
(2) /add word to line/
    L[M] <- L[M] + 1 + W[I]
    if L[M] <= D then goto (4)
(3) /start new line/
    L[M] <- L[M] - 1 - W[I]
    M <- M + 1, S[M] <- I, L[M] <- W[I]
(4) /test for completion/
    I <= I + 1, if I <= N then goto (2)
---------------------------------------------
```

The effect of algorith LINE-BY-LINE on a short sample paragraph from [^6], formatted 47 charactesr to a line, is given below. The surplus spaces in this paragraph have been distributed according to the alternate left and right fashion. Note that of the seven lines in the paragraph, the first five have 1, 2, 6, 10, 7 surplus spaces respectively. This means that in the fourth line, 10 spaces have to be distributed between six words, resulting in triple spacing between some of them. Pathological cases similar to this and worse abound in th eliterature. It would seem that this formatting can be improved by transfering the last words of the first, second, third and fourth lines to the beginning of the second, third, fourth and fifth lines respectively. This has been done in Sample Paragraph #2 where the surplus spaces are obviously more evenly distributed among the lines. In fact, the first paragraph has eight occurrences of triple spacing compared to two in the second.

Sample Paragraph # 1:


```
  We  live in a print-oriented society. Every day
  we produce a huge volume of  printed  material,
  ranging   from  handbills  to  heavy  reference
  books.   Despite   the   mushroom   growth   of
  electronic   media,   print  remains  the  most
  versatile and most widely used medium for  mass
  communication.
```

Sample Paragraph #2:

```
  We  live  in  a  print-oriented  society. Every
  day  we  produce  a  huge  volume  of   printed
  material,   ranging  from  handbills to   heavy
  reference books. Despite  the  mushroom  growth
  of  electronic  media,  print  remains the most
  versatile and most widely used medium for  mass
  communication.
```

## 3. A DYNAMIC PROGRAMMING SOLUTION

## 4. THE LINE BREAKER

## 5. EXTENSIONS

## 6. EXTENSIONS

## ACKNOWLEDGEMENTS

The author is grateful to the referees for their very helpful
suggestsions and to his colleagues Karl Ottenstein and John Lowther
for proof-reading several versions of the paper.

## REFERENCES

[^1]: A. V. Aho, J. E. Hopcraft & J. D. Ulman,<br/>
    The Design and ANalysis of Computer Algorithms, Addison Wesley, 1974, p69.

[^2]: K. Q. Brown,<br/> Dynamic Programming in Computer Science,
    Tech. Rep. CMU-CS_79-106, Dept of ComputerSc., Carnegie-Mellon
    Univ., Pittsburgh Pa, 1979.

[^3]: B. W. Kernighan, M. E. Lesk, J. F. Ossana,<br/> Unix Time SHaring
    System: Document Preparation, Bellw Systems Tecnical Journal
    57(6), July-Aug 198, pp 2115-2134.

[^4]: B. W. Kernighan, L. L. Cherry,<br/>
    A System for Typesetting Mathematics, CACM 18, March 1975, pp151-157.

[^5]: D. E. Knuth,<br/> TAU EPSILON CHI, A System for Technical Text,
    American Mathematical Society, Providence, Rhode Island, 1979

[^6]: J. Sachs,<br/> Economical Typesetting from Small Computer Text
    Files, Proc of the Third SYmposium on Small COmputers, sponsored
    by ACM SIGSMALL & SIGPC, Sept 1980, Pal ALto, California,
    pp184-188.

[^7]: J. Pearkins,<br/> FMT Reference Manual, University of ALberta
    Computing Service,s April 1976.

[^8]: TXTFORM - A Text Formatter,<br/> Dept of Computer Science, Purdue
    University, West Lafayette, Ind., 1979.

[^9]: DOC Processor Bulletin, Academic Computing Services, Michigan
    Technological University, Houghton, MI.

## APPENDIX


```
    PROCEDURE LINE-BY-LINE;
    (* D,L,M,N,S,W ARE EXPLAINED IN TABLE 1 *)

    BEGIN
        (* INITIALIZE *)
        M := 1;
        S[1] := 1;
        L[M] := W[1];

        FOR I := 2 TO N DO
        BEGIN

            (* ADD NEXT WORD TO CURRENT LINE *)
            L[M] :- L[M] + 1 + W[I];

            IF (L[M] > D) THEN
            BEGIN
                L[M] :- L[M] - 1 - W[I];

                (* START NEW LINE *)
                M := M + 1;
                S[M] := I;
                L[M] := W[I]
            END
        END
    END
```

```
    PROCEDURE DYNAMIC;

    (* COMPUTATION OF OPTIMAL COST C[1,N]
       C[I,J], F[I,J] EXPLAINED IN TABLE 1. *)

    BEGIN

        (* INTIALIZE VARIABLES *)
        FOR I := 1 TO N DO
        BEGIN
            FOR J := 1 TO N DO
            BEGIN
                F[I,J] := 0;
                C[I,J] := 0;
            END;
            F[I,J] := W[I];
            C[I,I] := 1 + 1 / W[I]
        END

        (* COMPUTE UPPER DIAGONAL OF L AND C
           IN REVERSE ROW ORDER *)
       FOR I : N-1 DOWNTO 1 DO
       BEGIN
           FOR J := I+1 TO N DO
           BEGIN

               (* CALCULATE FORMATTED LENGTH *)
               F[I,J] := F[I,J-1] + W[J] + 1;
               IF F[I,J] <= D THEN
               BEGIN

                   (* WORDS I TO J FIT ON LINE *)
                   IF J = N THEN C[I,J] := 2
                            ELSE C[I,J] := 1 + 1 / F[I,J]
               END
               ELSE
               BEGIN

                   (* WORDS I TO J HAVE TO BE SPLIT *)
                   C[I,J] := C[I,I] * C[I+1,J];
                   FOR K := I+1 TO J-1 DO
                   BEGIN
                       T := C[I,K] * C[K+1,J];
                       IF T< C[I,J] THEN C[I,J] := T
                   END
               END
           END
       END
    END;
```

```
    PROCEDURE LINE-BREAKER;

    (* COMPUTATION OF OPTIMAL STARTING INDICES P[I]
       FOR M > 2.
       ASSUME S[I], E[I], L[I] (DEFINED IN TABLE 1)
       HAVE BEEN COMPUTED. X,Y,Z ARE USED TO KEEP
       TRACK OF REQUIRED LENGTHS.
       INFINITE IS ANY NUMBER LARGER THAN MAXIMUM
       POSSIBLE COST c[I] *)

    BEGIN

        c[S[M]] := 2.0;

        (* LOOP ON LINES BACKWARDS *)
        FOR I := M-1 DOWNTO 1 DO
        BEGIN

            X := L[I] - 1 - W[S[I]];

            (* LOOP OVER I-TH SLACK *)
            FOR J := S[I] DOWNTO E[I] DO
            BEGIN

                X := X + 1 + W[J];
                Y := X + 1 + W[S[I+1]];
                c[J] := INFINITE;

                (* LOOP OVER (I+1)-THE SLACK *)
                FOR K := S[I+1] DOWNTO E[I+1] DO
                BEGIN
                    Y := Y - 1 - W[K];
                    IF Y<= D THEN
                    BEGIN

                        (* UPDATE c[J] *)
                        Z := (1 + 1 / Y) * c[K];
                        IF Z < c[J] THEN
                        BEGIN
                            c[J] := Z;
                            P[J] := K
                        END
                    END
                END
            END
        END;

        (* RETRIEVE OPTIMAL STARTING INDECIES *)
        P[M] := S[M];  J := P[1];  P[1] := 1;
        FOR I := 2 TO M-1 DO
        BEGIN
            K := P[I];  P[I] := J;  J := K
        END
    END;
```
