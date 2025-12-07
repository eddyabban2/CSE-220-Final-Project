/* Minimal perceptron predictor implementation */

#include "cpu/pred/perceptron.hh"

#include "base/bitfield.hh"
#include "debug/Branch.hh"

namespace gem5
{
namespace branch_prediction
{

PerceptronBP::PerceptronBP(const PerceptronBPParams &params)
    : BPredUnit(params),
      tableSize(params.tableSize),
      historyLength(params.historyLength),
      weightBits(params.weightBits)
{
    if (!isPowerOf2(tableSize)) {
        fatal("PerceptronBP: tableSize must be a power of two\n");
    }
    // masks and per-thread state
    historyMask = (historyLength >= 32) ? 0xFFFFFFFFu : ((1u << historyLength) - 1);

    // allocate weights
    unsigned cols = historyLength + 1; // bias + history weights
    weights.resize(tableSize);
    for (unsigned i = 0; i < tableSize; ++i) {
        weights[i].assign(cols, 0);
    }

    globalHistory.resize(numThreads, 0);
}

bool PerceptronBP::lookup(ThreadID tid, Addr branch_addr, void * &bp_history)
{
    // index table by PC (shifted by instShiftAmt)
    unsigned idx = (branch_addr >> instShiftAmt) & (tableSize - 1);

    unsigned ghr = globalHistory[tid] & historyMask;

    // compute perceptron output
    int sum = weights[idx][0];
    for (unsigned i = 0; i < historyLength; ++i) {
        int h = ((ghr >> i) & 1) ? 1 : -1;
        sum += weights[idx][i+1] * h;
    }

    // create history object
    PerceptronHistory *h = new PerceptronHistory;
    h->ghr = ghr;
    h->index = idx;
    bp_history = (void*)h;
    assert(bp_history);

    return sum >= 0;
}

void
PerceptronBP::updateHistories(ThreadID tid, Addr pc, bool uncond, bool taken,
                              Addr target, const StaticInstPtr &inst,
                              void * &bp_history)
{
    // update global history for all branches
    globalHistory[tid] = ((globalHistory[tid] << 1) | (taken ? 1 : 0)) & historyMask;

    // nothing else to do for this simple predictor
}

void
PerceptronBP::update(ThreadID tid, Addr branch_addr, bool taken,
                     void * &bp_history, bool squashed,
                     const StaticInstPtr & inst, Addr target)
{
    if(!bp_history)
        return;
    PerceptronHistory *h = (PerceptronHistory *)bp_history;

    if (squashed) {
        // restore saved history
        globalHistory[tid] = h->ghr;
        delete h;
        bp_history = nullptr;
        return;
    }

    unsigned idx = h->index;
    unsigned old_ghr = h->ghr & historyMask;

    // recompute output
    int sum = weights[idx][0];
    for (unsigned i = 0; i < historyLength; ++i) {
        int bit = ((old_ghr >> i) & 1) ? 1 : -1;
        sum += weights[idx][i+1] * bit;
    }

    bool pred = sum >= 0;
    int y = sum;

    // simple training: update when wrong or weak (|y| <= threshold)
    int threshold = 0; // minimal threshold for this simple predictor
    if (pred != taken || abs(y) <= threshold) {
        int label = taken ? 1 : -1;
        int max_w = (1 << (weightBits - 1)) - 1;

        // update bias
        int newb = weights[idx][0] + label;
        if (newb > max_w) newb = max_w;
        if (newb < -max_w) newb = -max_w;
        weights[idx][0] = newb;

        for (unsigned i = 0; i < historyLength; ++i) {
            int bit = ((old_ghr >> i) & 1) ? 1 : -1;
            int delta = label * bit;
            int w = weights[idx][i+1] + delta;
            if (w > max_w) w = max_w;
            if (w < -max_w) w = -max_w;
            weights[idx][i+1] = w;
        }
    }

    // history already updated in updateHistories at prediction time; free
    delete h;
    bp_history = nullptr;
}

void
PerceptronBP::squash(ThreadID tid, void * &bp_history)
{
    PerceptronHistory *h = static_cast<PerceptronHistory *>(bp_history);
    // restore history
    globalHistory[tid] = h->ghr;
    delete h;
    bp_history = nullptr;
}

} // namespace branch_prediction
} // namespace gem5
