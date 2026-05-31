# data

`golden_dataset.json`

A small set of real field situations, each with a known right call. This does
not come from the dataset. It comes from how an experienced rep would actually
handle the situation, the kind of judgement that does not show up in a CSV.

Eight cases right now, covering prioritisation, next best action, anomaly
handling, and outcome learning. Each case has:

  situation   the setup, with the relevant numbers
  expected    the right call
  reasoning   why that is the right call, in plain words
  tests       which capability it probes

The point of this file is to measure the model against human judgement, not just
against held out data. A model can score well on historical data and still make
dumb calls in situations the data never covered. The golden set catches that.

How it gets used: src/evaluation.py reads this file. Pass it a scorer function
that maps a situation to a decision and it reports how many the model gets right.
Without a scorer it just reports what is in the set, which doubles as
documentation of what "a good recommendation" means here.

Add more cases over time. Every time you talk to a rep and hear "oh the system
would never get this one right", write it down as a case. That is how the eval
set stays honest and grows teeth.
