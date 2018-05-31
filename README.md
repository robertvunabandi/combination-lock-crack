# Combination Lock Cracker

This project is an attempt at cracking combination lock combos. 

***NOTE:*** *This project is for purely educational purpose. In fact, it is an attempt at showing why combination locks are unsafe!*

## Hypothetical Scenario

Let's say that a person, let's call this person **`A`**, has a bike and of course a bike-lock. His or her bike-lock is a 4-digit password system. More precisely, it's a system where numbers are placed in a rotating manner, like this image here:
![bike-lock](images/bike-lock.jpg)  
> *image source: https://www.dormco.com/Combination_Cable_Bike_Lock_Master_Lock_Dorm_p/gh2-1-3-8114d.htm*

Imagine another person, let's call this person **`B`**, wants to steal **`A`**'s bike. Now, **`B`** is intelligent, so he will try not to get caught. To do so, he will try to figure out **`A`**'s bike-lock combination. More precisely, **`B`** will stalk **`A`**, and every time locks his or her bike the the bike-lock, **`B`** will do the follwoing threw actions:

- Observe what combo is left on the lock
- Attempt to unlock the bike-lock without changing the combo
	- If it unlocks, **`B`** takes the bike
	- If it doesn't, **`B`** records the combo that he has seen (in this case, **`A`**, as one can expect, would have shuffled the combo)

Eventually, **`B`** will have a long list of `n` different lock combos (`n` being an integer), with which **`B`** hopes to analyze in order to figure out the true combo that will unlock the bike. 

NOTE: You can read the [article I wrote about this {{TODO:LINK_TO_MEDIUM_ARTICLE_WHEN_PUBLISHED}}](Link_here) on medium.

## Analysis

Before you jump to the conclusion that this is hopeless, let me attempt to reason you out otherwise. We observe the following.

If **`A`** desires not lose his or her bike, **`A`** will *always* shuffle the combo. Let's assume that is true. Then, there are only two safe ways to shuffle the bike-lock combo (in order of highest safety to lowest):

1. Shuffling the combo to the same exact number every single time
2. Shuffling the combo randomly using a random number generator

Assuming **`A`** uses neither of these shuffling methods, **`A`**'s shuffling *will not be random*, and that is key to this entire project. Whenever data is not random, there exists an algorithm that can exploit it to extract useful information out of it, and that is likely the most important aspect of this entire project.

**Why is (1) the safest solution?** If we are using data analysis algorithms to figure out the code, the more data we have, the better. However, (1) doesn't help because observing the same information twice in a row does not add any new informations! Although we'd be use that the combo that we always see is not the correct one, that rules out 1 out of too many possibilities. Most locks have 4 to 5 digits, so it's one out of 10000 to 100000 combinations (assuming the combinations only have numbers).

**Why is (2) also safe, although not as safe as (1)?** Using a truly random number prevents any data analysis algorithm to find a pattern or structure to the data. However, the problem with this is that given enough time, **`B`** will be able to rule out enough combinations to reduce the set of possible true codes to a small subset of the entire sample space. However, this is still safe because it's simply not practice to wait this long for a bike or anything else. Assuming 4 digits, there are 10000 possible codes. Assuming **`B`** is able to get at most 5 shuffled combos per day, it will still take **`B`** at least about 5.5 years to rule out every single code and likely more due to the fact that **`B`** will start rereading the same combo multiple times. 

So, with that in mind, we are ready to tackle this challenge.

## Probabilistic Approach

At this point, let's think of the true combo as `X`, and let's think of the shuffled combo observations as `y_i` for `i` in the set `{1, 2,...,n}` (i.e., we've made `n` observations). Our goal is to use the `y_i`'s in order to get closer to `X`. 

The model we will use is the [naive Bayes classifier (NBC)](https://en.wikipedia.org/wiki/Naive_Bayes_classifier). Modeling this problem as an NBC makes sense. NBC require that there is one latent/hidden variable, which is `X` in our case. Additionally, NBC's require that the observations made are each independent of each other, which also makes sense in this case. Every time **`A`** needs to unlock the lock, **`A`** enters the true code. Then, when they lock it again, they reshuffle. It doesn't make much sense for **`A`** to pick the new shuffled code based on what the previous shuffled code. However, note that we can't assume that every human being will act the way we expect them to act, so there is a non-zero chance that someone does shuffle their code based on the previous shuffled code. Nevertheless, we will assume that this does not happen by assuming that the observations are independent of each other.

So, we get the following image:
![Naive Bayes Classifier Representation](images/nbc.jpg)
> *image source: I took this photo.*

Initially, we have no idea what `X` really is. So, it's in our best interest to guess that the probability that `X` is any number `s` in the set `S = {0000, 0001, ..., 9998, 9999}` is uniform over that set. (Note that we use lower case `s` for one of the number, and note that we use 4-digit numbers in the set. However, this can still be extended to having `d` digits where `d > 0` is an integer. For more clarity, we use `d = 4`). 

Let's assume that we are at a point that for any `s` in the set `S`, the probability that `X = s` is `p_s`. At this point, we also have made the observation `y_i`. So, we need to update, for every possible `s`, their probabilities. I.e., what is the probability that `X = s` given that we have observed `y_i` for each possible `s` and the same `y_i`? That is what we update the new probability that `X = s` to. So, we do the following:

- Loop over each `s` in the set `S = {0000, 00001, ..., 9998, 9999}`
    -   Update the probability that `X = s` given that we observed `y_i` using the following

        ```
        p(X=s|y_i) = p(y_i|X=s) * p(X = s) / p(y_i)
        ```
        
        Note that we have use [Bayes' rule](https://en.wikipedia.org/wiki/Bayes%27_theorem) above to figure. Then, using the [law of total probability](https://en.wikipedia.org/wiki/Law_of_total_probability), we can update `p(y_i)` in the following way:

        ```
        p(y_i) = sum_over_every s in S: p(y_i|X=s) * p(X=s) / p(y_i)
        ```

        We are justified to use the law of total probability because if `X = s`, then `X` cannot equal any other values in the sample space `S` that is not `s`. I.e., each of the `s`'s form a partition of the sample space. 

In the above algorithm, we already know `P(X=s)`. This number is `p_s` that we were given. However, what do we do with `p(y_i|X=s)`? This is the probability of observing `y_i` given that `s` is the true code (i.e. given that `X = s`). 

Intuitively, if `y_i` equals `s`, then it is extremely unlikely to observe `y_i` because in that case it'd be the true code. Thus, `p(y_i=s|X=s)` is an extremely small number. With the assumption that **`A`** above always shuffle, this quantity is `p(y_i=s|X=s) = 0`. To be clear, the only way we know that `y_i` is not the code is because we assume we are able to always check for ourselves before we do the recording. However, it is possible that we don't always have that opportunity. 

Another intuition is that if we see a shuffled combo, we should expect that number to be far away from the true code. For example, if the true code is `5555`. We should be more likely to see `1234` than `5554` because `5554` is so close to the true code. Psychologically speaking, the person who shuffles the code will always try to stay away as far as possible to the true code.

Finally, one can easily see that from those two intuitions above, thinking about `p(y_i|X=s)` is far easier than thinking about `p(X=s|y_i)`. In fact, the attempt to solve this problem is for us to *define* how `p(y_i|X=s)` given every possible pairs of `y_i` and `s`, both of which come from the same sample space `S`. So, that is what we do in the following sections.

## Defining the Observation Model

It is evident that choice of observation model will dictates how close we get to the true combo. The **observation model** is simply a fancy term for the probability function `p(y_i|X=s)` (the probability of observing `y_i` given that the true code is `s` for every possible `y_i` and `s` both in the set `S`). They call it observation model because it is a model that dictates how we update our belief after having observed an observation.

So, let's dive into some of the observation models we attempted to solve this problem.

### Black And White Model (BWM)

TODO.

### Difference Distance Model (DDM)

TODO.

### Edit Distance Model (EDM)

TODO.

## Critics on our Approach

The observation models that we have describes are not the only possible ones. One could, if he or she wanted, come up with more complex models that solve this problem more efficiently. I spent a lot of time to come up with these, but I hope they give you some perspectives into other things that we can do. If you discover another solution that works well, please hit me up I'd like to know. Anyway, let's discuss the other possible ways of solving this problem.

### Using Digit Probabilities

One way to change the way we approach the problem is to look at each observation as an observation for each individual digits. So, let's say the true code is `5555` and we observe `1111`. Instead of updating the overall distribution of `s` in the set `S`, we update the distribution of the first, second, third, and fourth digits separately. Also, for each digits at index `k`, we can think of the true digit at index `k` as being the latent random variable `X_k` and we just made the observation `y_i^(k)` (note that the `^(k)` is not an exponent; it's a superscript. It's just saying, look at digit at index `k` of the new observation `y_i`). Then, we can treat solve for index `k` using an naive Bayes classifier (NBC). 

One question that this raises is that the relationship between each digit is definitely not independent. Whenever someone picks a code, they choose a code they like or relate to. So, that means that we could possibly learn about how digit at index `k` relates do digits at index `k+1` and `k-1` (or every other digits as well). 

Anyway, I actually tried the digit model using an observation model such that the probability of observing `y_i^(k)` given that the true digit is `X_k = s_k` is `1/10` if `y_i^(k) = s_k` and `9/10` otherwise. This worked pretty well, and it worked really close to the difference distance model. 

### Using Digit Relativities

Digit relativities is essentially the last point of the above subsection on Using Digit Probabilities. We could also use an NBC here and say that for the digits at index `j` and index `k`, their distance (how far they are from each other, i.e. the absolute value of their difference) is a random variable `X_(j,k)`. Then, whenever we observe `y_i`, we look at the difference for the index `j` and `k` in that observation, let's call it `y_i^(j,k)` (note that this is also not an exponent; it's a superscript again). So, we could use an NBC and update our belief about what `X_(j,k)` should be after having observed `y_i^(j,k)`. 

I personally feel like although this relativity could be non-random, it seems like it's very insignificant based on the observations. Whenever the person shuffles, the difference we observe in the shuffled combo could be close to random even when the person is not shuffling randomly.

### Using A Different Core Model

Notice that by choosing to use a naive Bayes classifier (NBC), we have restricted the way we attack this problem. *That is not the only way to solve this problem*. 

One other model that we could have done is using a [neural network (NN)](https://en.wikipedia.org/wiki/Artificial_neural_network). The way this would work is to put a hard a number to the number of data points that we have to collect. That is, for example, for each combination lock that person **`B`** is trying to crack, person **`B`** will need to collect `d` combo readings. The greater the value `d`, the better. Then, we can use the `d` numbers as input layer. Then, have multiple hidden layers, and finally, have a softmax output layer that outputs the probability of each number in the set `S`. I am not sure how well this would work, but one of the very problem with using an NN is that it requires a LOT of data to train. Usually, in the order of `10,000`. For our case, that'd be `10,000` times `d` total readings. If `d` was `20` for example, then that amounts to `200,000` total readings for about `10,000` (ideally) different combos of the *same* digit length. It's also problematic that they have to come from the *same* digit length because if we wanted to generalize to any length, then we need separate data for each length. That's a pain when we're not even guaranteed that it'd work well. 

Another way would be not to assume that the observations were independent of each other. There is a very subtle thing that happens with this. When using an NBC, whenever we observe `y_i`, we update the distribution based on `y_i` and based on the distribution that we have updated so far. In a way, the distribution that we have so far somewhat contains *some* informations about all the previous `y`'s. However, it doesn't necessarily contains *all* information about them. In this sense, one could make a model such that whenever we update our belief, we update on the relationship between all the `y`'s that we have observed so far. I am not sure exactly how to approach the problem this way, but it is certainly possible. 

































