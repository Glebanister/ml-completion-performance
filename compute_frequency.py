import argparse

from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict
from itertools import accumulate


@dataclass
class PsiElementFrequency:
    level: int
    name: str
    freqency: int

    @classmethod
    def from_repr(cls, repr: str):
        l, n, f = repr.split()
        return PsiElementFrequency(int(l), n, int(f))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('freq', type=Path, help='Path to the frequencies file')
    parser.add_argument('threshold', type=float,
                        help='Threshold for rarely used classes cut-off')
    parser.add_argument('--report', action='store_true', help='Print full report')
    args = parser.parse_args()
    psi_freq_per_level: Dict[int, List[PsiElementFrequency]] = {}
    with args.freq.open('r') as freq_file:
        for freq in [PsiElementFrequency.from_repr(line) for line in freq_file.readlines()]:
            psi_freq_per_level.setdefault(freq.level, []).append(freq)
    for level in psi_freq_per_level.keys():
        cur_level_psi_freq = sorted(
            psi_freq_per_level[level], key=lambda f: f.freqency, reverse=True)
        fqs = list(map(lambda fq: fq.freqency, cur_level_psi_freq))
        total_usages = sum(fqs)
        relative_usages = map(lambda fq: fq / total_usages, fqs)
        passed_threshold = next(filter(
            lambda p: p[1] >= args.threshold,
            enumerate(accumulate(relative_usages))
        ))[0] + 1

        if args.report:
            print(f"Level {level}:\n", ', \n    '.join(map(lambda fq: f"\"{fq.name}\": {fq.freqency}/{total_usages}", cur_level_psi_freq[:passed_threshold])), end='\n')
            passed_usages = sum(map(lambda f: f.freqency, cur_level_psi_freq[:passed_threshold]))
            print(f"In total: {passed_usages}/{total_usages}, {passed_usages * 100 / total_usages:.2f}%")
        else:
            print(f"Level {level}:")
            for f in cur_level_psi_freq[:passed_threshold]:
                print(f"    \"{f.name}\",")
        print()

if __name__ == '__main__':
    main()
