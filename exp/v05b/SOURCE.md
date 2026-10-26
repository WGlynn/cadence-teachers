EXP-71 imports Bernhard Mueller's V0.5B runner unchanged. It is not copied into this repo: the
source repository (ali12mahmood12345-boop/cadence-stone-age) has not chosen a license yet.
To reproduce, fetch it here:

    git clone https://github.com/ali12mahmood12345-boop/cadence-stone-age.git /tmp/csa
    git -C /tmp/csa fetch origin pull/1/head:pr1 && git -C /tmp/csa checkout 5f038a3
    cp /tmp/csa/research/attention-v0.5b/{run_v05b.py,split_check.py} exp/v05b/
    cp /tmp/csa/research/attention-v0.5b/results/v05b_59101.json exp/v05b/bernhard_v05b_59101.json

Commit 5f038a3 = "Attention V0.5B: self-contained runner and a four-founder local pilot" (PR #1).
