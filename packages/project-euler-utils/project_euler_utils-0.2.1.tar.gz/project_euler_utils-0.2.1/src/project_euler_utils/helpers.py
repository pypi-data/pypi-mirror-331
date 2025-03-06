class Collatz:

    def __init__(self):
        self.lengths = {}

    def get_collatz(self, num):

        if num <= 2:
            return num

        if num in self.lengths:
            return self.lengths[num]

        chain_length_at_num = 0

        if num % 2 == 0:
            chain_length_at_num = self.get_collatz(num // 2) + 1
        else:
            chain_length_at_num = self.get_collatz((num * 3) + 1) + 1

        self.lengths[num] = chain_length_at_num

        return self.lengths[num]
