/*
 * Minimal perceptron branch predictor for gem5
 *
 * This is a lightweight, educational perceptron implementation. It is
 * intentionally simple: a table of perceptrons indexed by PC, with simple
 * saturating integer weights and a global taken-history register per thread.
 */

#ifndef __CPU_PRED_PERCEPTRON_HH__
#define __CPU_PRED_PERCEPTRON_HH__

#include <vector>

#include "cpu/pred/bpred_unit.hh"
#include "params/PerceptronBP.hh"

namespace gem5
{
namespace branch_prediction
{

class PerceptronBP : public BPredUnit
{
  public:
    PerceptronBP(const PerceptronBPParams &params);

    // Base class methods.
    bool lookup(ThreadID tid, Addr branch_addr, void* &bp_history) override;
    void updateHistories(ThreadID tid, Addr pc, bool uncond, bool taken,
                         Addr target, const StaticInstPtr &inst,
                         void * &bp_history) override;
    void update(ThreadID tid, Addr branch_addr, bool taken, void *&bp_history,
                bool squashed, const StaticInstPtr & inst,
                Addr target) override;
    void squash(ThreadID tid, void * &bp_history) override;

  protected:
    struct PerceptronHistory {
        unsigned int ghr;
        unsigned int index;
    };

  private:
    // Config params
    const unsigned tableSize;
    const unsigned historyLength;
    const unsigned weightBits;

    // runtime masks
    unsigned historyMask;

    // Predictor storage: tableSize x (historyLength + 1) weights per entry.
    // weights[i][0] is bias weight.
    std::vector<std::vector<int>> weights;

    // Per-thread global history
    std::vector<unsigned int> globalHistory;
};

} // namespace branch_prediction
} // namespace gem5

#endif // __CPU_PRED_PERCEPTRON_HH__
