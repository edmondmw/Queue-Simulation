import simpy
import random
import math

RANDOM_SEED = 29
SIM_TIME = 1000000
MU = 1

class queue:
		def __init__(self, env, arrival_rate, buffer_size):
			self.server = simpy.Resource(env, capacity = 1)
			self.env = env
			self.arrival_rate = arrival_rate
			self.queue_len = 0
			self.buffer_size = buffer_size
			self.arrival_count = 0
			self.drop_count = 0

		def process_packet(self, env):
				with self.server.request() as req:
						yield req
						yield env.timeout(random.expovariate(MU))
						self.queue_len -= 1

		def packets_arrival(self, env):
			while True:
					yield env.timeout(random.expovariate(self.arrival_rate))
					self.arrival_count += 1
					if self.queue_len == self.buffer_size:
						self.drop_count += 1
					else:
						self.queue_len += 1
						env.process(self.process_packet(env))
					
					
def main():
		arrival_rates = [0.2, 0.4, 0.6, 0.8, 0.9, 0.99]
		buffer_sizes = [10, 50]
		random.seed(RANDOM_SEED)
		env = simpy.Environment()
		loop_count = 0

		for b in buffer_sizes:
			for a in arrival_rates:
				loop_count += 1
				myQueue = queue(env, a, b)
				env.process(myQueue.packets_arrival(env))
				env.run(until = SIM_TIME*loop_count)
				#probability of packet loss
				Pd = myQueue.drop_count/myQueue.arrival_count
				print('Lambda: ' , a, '  B:', b,'  Pd:',Pd )

		input("prompt: ")

if __name__ == '__main__': main()

