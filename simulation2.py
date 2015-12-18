# This is a simpy based  simulation of a M/M/1 queue system

import random
import simpy
import math

RANDOM_SEED = 29
SIM_TIME = 1000000
MU = 1
B = math.inf
N = 10

class ethernet:
	def __init__(self, env, queue_list):
		self.env = env 
		self.queue_list = queue_list
		self.current_slot = 0
		self.successes = 0
		self.collisions = 0
	
	def exponential_backoff(self, env):
		while True:
			transmitting_queues = []
			#check if a host wants to transmit during current slot	
			for q in self.queue_list:
				#print(q.queue_len, ' ', q.slot_number, ' ', q.number_collisions)
				#check if the current slot number needs updating
				if q.queue_len > 0 and q.slot_number < self.current_slot:
					q.slot_number = self.current_slot + 1
				#host wants to transmit during this slot
				if q.slot_number == self.current_slot and q.queue_len >= 1:
					transmitting_queues.append(q)
			#if only one host with that slot number then we can transmit
			if len(transmitting_queues) == 1:
				#print('SUCCESS')
				transmitting_queues[0].queue_len -= 1
				transmitting_queues[0].slot_number = self.current_slot + 1
				transmitting_queues[0].number_collisions = 0						
				self.successes += 1
			#collision
			elif len(transmitting_queues) > 1:				
				self.collisions += 1
				#change slot numbers and collisions
				for q in transmitting_queues:
					k = min(q.number_collisions, 10)
					randomNum = random.uniform(0,1)
					r = round(randomNum*2**k) 
					q.slot_number = q.slot_number + r + 1
					q.number_collisions += 1

			yield env.timeout(1)
			self.current_slot += 1 

	def linear_backoff(self, env):
		while True:
			transmitting_queues = []
			#check if a host wants to transmit during current slot	
			for q in self.queue_list:
				#check if the current slot number needs updating
				if q.queue_len > 0 and q.slot_number < self.current_slot:
					q.slot_number = self.current_slot + 1
				#host wants to transmit during this slot
				if q.slot_number == self.current_slot and q.queue_len > 0:
					transmitting_queues.append(q)
			#if only one host with that slot number then we can transmit
			#decrement L, increment S, and reset N
			if len(transmitting_queues) == 1:
				transmitting_queues[0].queue_len -= 1
				transmitting_queues[0].slot_number = self.current_slot + 1
				transmitting_queues[0].number_collisions = 0
				self.successes += 1
			#collision
			elif len(transmitting_queues) > 1:
				self.collisions += 1
				#change slot numbers and collisions
				for q in transmitting_queues:
					k = min(q.number_collisions, 1024) 
					randomNum = random.uniform(0,1)
					r = round(randomNum*k)
					q.slot_number = q.slot_number + r + 1
					q.number_collisions += 1

			yield env.timeout(1)
			self.current_slot += 1 

""" Queue system  """		
class server_queue:
	def __init__(self, env, arrival_rate, Packet_Delay, Server_Idle_Periods,buffer_size, slot_number):
		self.server = simpy.Resource(env, capacity = 1)
		self.env = env
		self.queue_len = 0
		self.flag_processing = 0
		self.packet_number = 0
		self.sum_time_length = 0
		self.start_idle_time = 0
		self.arrival_rate = arrival_rate
		self.Packet_Delay = Packet_Delay
		self.Server_Idle_Periods = Server_Idle_Periods
		self.buffer_size = buffer_size;
		self.total_no_packets = 0
		self.discards = 0
		self.slot_number = slot_number
		self.number_collisions = 0		
		

	def process_packet(self, env, packet):
		#with self.server.request() as req:
			start = env.now
			#yield req
			#yield env.timeout(random.expovariate(MU))
			latency = env.now - packet.arrival_time
			self.Packet_Delay.addNumber(latency)
			#print("Packet number {0} with arrival time {1} latency {2}".format(packet.identifier, packet.arrival_time, latency))
			self.queue_len -= 1
			self.slot_number += 1
			self.number_collisions = 0

			if self.queue_len == 0:
				self.flag_processing = 0
				self.start_idle_time = env.now
				
	def packets_arrival(self, env):
		# packet arrivals	
		while True:
			     # Infinite loop for generating packets
				yield env.timeout(random.expovariate(self.arrival_rate))
			     # arrival time of one packet
				self.total_no_packets += 1

				if self.queue_len < self.buffer_size:
					self.packet_number += 1
	                  # packet id
					arrival_time = env.now  
	                #print(self.num_pkt_total, "packet arrival")
					new_packet = Packet(self.packet_number,arrival_time)
					if self.flag_processing == 0:
						self.flag_processing = 1
						idle_period = env.now - self.start_idle_time
						self.Server_Idle_Periods.addNumber(idle_period)
						#print("Idle period of length {0} ended".format(idle_period))
					self.queue_len += 1
					#env.process(self.process_packet(env, new_packet))
					
				else:
					self.discards += 1
				


""" Packet class """			
class Packet:
	def __init__(self, identifier, arrival_time):
		self.identifier = identifier
		self.arrival_time = arrival_time
		

class StatObject:
    def __init__(self):
        self.dataset =[]

    def addNumber(self,x):
        self.dataset.append(x)
    def sum(self):
        n = len(self.dataset)
        sum = 0
        for i in self.dataset:
            sum = sum + i
        return sum
    def mean(self):
        n = len(self.dataset)
        sum = 0
        for i in self.dataset:
            sum = sum + i
        return sum/n
    def maximum(self):
        return max(self.dataset)
    def minimum(self):
        return min(self.dataset)
    def count(self):
        return len(self.dataset)
    def median(self):
        self.dataset.sort()
        n = len(self.dataset)
        if n//2 != 0: # get the middle number
            return self.dataset[n//2]
        else: # find the average of the middle two numbers
            return ((self.dataset[n//2] + self.dataset[n//2 + 1])/2)
    def standarddeviation(self):
        temp = self.mean()
        sum = 0
        for i in self.dataset:
            sum = sum + (i - temp)**2
        sum = sum/(len(self.dataset) - 1)
        return math.sqrt(sum)


def main():
	arrival_rates = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]
	random.seed(RANDOM_SEED)
	
	#exponential backoff
	print('EXPONENTIAL')
	for a in arrival_rates:
		env = simpy.Environment()
		Packet_Delay = StatObject()
		Server_Idle_Periods = StatObject()

		#create the 10 queues for each host
		queue_list = []
		for i in range(0,N):
			queue_list.append(server_queue(env,a,Packet_Delay, Server_Idle_Periods, B, 0))
			env.process(queue_list[i].packets_arrival(env))
				
		exponentialEthernet = ethernet(env, queue_list)
		env.process(exponentialEthernet.exponential_backoff(env))
		env.run(until = SIM_TIME)
		print('arrival: ', a, ' throughput: ', exponentialEthernet.successes/exponentialEthernet.current_slot,
			' successes: ', exponentialEthernet.successes, ' collisions: ', exponentialEthernet.collisions) 
		
	#linear backoff	
	print('LINEAR')	
	for a in arrival_rates:
		env = simpy.Environment()
		Packet_Delay = StatObject()
		Server_Idle_Periods = StatObject()

		#create the 10 queues for each host
		queue_list = []
		for i in range(0,N):
			queue_list.append(server_queue(env,a,Packet_Delay, Server_Idle_Periods,B, 0))
			env.process(queue_list[i].packets_arrival(env))
				
		linearEthernet = ethernet(env, queue_list)
		env.process(linearEthernet.linear_backoff(env))
		env.run(until = SIM_TIME)
		print('arrival: ', a, ' throughput: ', linearEthernet.successes/linearEthernet.current_slot, 
			' successes: ', linearEthernet.successes, ' collisions: ', linearEthernet.collisions)
		
if __name__ == '__main__': main()
