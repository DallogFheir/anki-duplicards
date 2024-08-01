# Anki DupliCards

<img src="icon.png" width="50px" >

An Anki add-on allowing you to merge cards while adding them.

## Use case

Assume you're learning French and you create the following cards:

- front: _voler_, back: _to fly_
- front: _voler_, back: _to steal_
- front: _piquer_, back: _to steal_

Now, if you're shown _voler_, it'd be nice if you knew both meanings. And vice versa, if you're shown _to steal_, you should know both French words.

You could edit an already existing card to add a second meaning, but that would be tedious and not update the scheduler.

This add-on solves the problem. For every card added, it searches for cards with the same front or back, then updates those cards and marks them as new. So in the above situation, you would have 4 cards:

- front: _voler_, back: _to fly, to steal_
- front: _piquer_, back: _to steal_
- front: _to fly_, back: _voler_
- front: _to steal_, back: _voler, piquer_

Adding (_piquer_, _to sting_) would update the back of the second card to _to steal, to sting_, and add a new card (_to sting_, _piquer_).

## How to use

The add-on only merges the cards of the note type _X-DupliCard_. This type will be added on startup, if it doesn't exist. Functionally it's the same as the basic card, except it also has the `Type` field, which can be used to distinguish the "sides" of the card. The type can be either `FB` (front-back) or `BF` (back-front).

## Warnings

This add-on monkey-patches the `Collection.add_note` method. It should not affect other cards, but if it does, please report an issue.

A drawback of this add-on is that it creates 2 separate basic cards for each word-meaning pair, so if you make a typo, for example, you have to correct both cards.

## Changelog

- 2.0.0 [current]
  - added `Type` field to the card
- 1.0.2
  - now only cards in the same deck as the added card are updated
- 1.0.1
  - notes preserve tags now
  - X-DupliCard note type is added on installation
  - fixed cursor jumping to the next field while adding a card
- 1.0.0
