import sys
from collections import OrderedDict

class ProcessManager:
	def __init__(self):
		self.MAX_NUMBER_BLOCKS = 16
		self.PCB = PCB()
		self.RCB = RCB(4)
		self.RL = [[0],[],[]]
		self.current_priority = 0 #current process priority
		self.number_control_blocks = 0 #number of process after create and destroy
		self.head = self.RL[self.current_priority][0]

	def reset(self):
		self.PCB = PCB()
		self.RCB = RCB(4)
		self.RL = [[0],[],[]]
		self.current_priority = 0
		self.number_control_blocks = 0
		self.head = self.RL[self.current_priority][0]


	def findindex(self, j):
		i = [i for i, x in enumerate(self.PCB.control_blocks) if (x.number_id == j)]
		#print(i[0], 'called findindex function')
		return(i[0])


	#FUNCTION #1
	def create(self, priority):
		#Error check
		if priority==0:
			return none

		#checked this error condition
		if self.number_control_blocks == self.MAX_NUMBER_BLOCKS:#Attempting to create more than n processes
			#print('Creating more than n processes')
			return(-1)

		self.PCB.number_control_blocks = self.PCB.number_control_blocks + 1
		#this number will only increase assigning every new control block the latest number of created
		#control block, example once block 4 is created, another control block can never be known as block 4

		#relevant values within different data structures
		unique_id = self.PCB.number_control_blocks
		parent_process = self.RL[self.current_priority][0]
		parent_index = self.findindex(parent_process)

		self.PCB.control_blocks.append(PControlBlock(unique_id, priority, parent_process,[]))
		#figure out why I have to place an explicit empty list in this create when constructor of class already has this

		self.RL[priority].append(unique_id)

		self.PCB.control_blocks[parent_index].children.append(unique_id)

		self.number_control_blocks = self.number_control_blocks + 1
		# this is for the current total of control blocks currently in this PCB after adding and destroying
		#print('process '+ str(unique_id) + ' created')
		self.scheduler()
		self.head = self.RL[self.current_priority][0]




	#FUNCTION #2
	def destroy(self,j:int, parent:int=None):#destroying a process in the PCB
		#print('entered destroy function for '+ str(j))
		#print(self.PCB.control_blocks[j].parent, end= '= parent of destroyed process')
		i = self.findindex(j)
		#checked this error condition
		if(self.PCB.control_blocks[i].parent != self.RL[self.current_priority][0] and#must either be parent
		   self.PCB.control_blocks[i].number_id != self.RL[self.current_priority][0] and#or itself
		   self.PCB.control_blocks[i].parent != parent):#or ancestor
			#current running process or head of RL[current_priority] should be either
			#the parent or an ancestor of any of the processes being destroyed.
			#print('Current running process is not the parent of j in destroy(j) or itself')
			return(-1)


		#for all k in children of j destroy(k) X
		if len(self.PCB.control_blocks[i].children)>0:
			number_of_children = len(self.PCB.control_blocks[i].children)
			for child in range(0,number_of_children):
				self.destroy(self.PCB.control_blocks[i].children[-1], j)
				#workaround to delete all children of process, by using last element being
				#the list elements in indices remain unmodified.

		#remove j from parent's list (ie. Process j is removed from the list of children of parent process.) X
		parent = self.PCB.control_blocks[i].parent
		parent_index = self.findindex(parent)
		#print(self.PCB.control_blocks[parent].children, end='=self.PCB.control_blocks[parent].')

		self.PCB.control_blocks[parent_index].children.remove(j)
		#print(self.PCB.control_blocks[parent].children, end='=self.PCB.control_blocks[parent].')

		#?remove j from RL or waiting list
		#print(self.RL,end='self.RL')
		if j in self.RL[self.PCB.control_blocks[i].priority]:
			self.RL[self.PCB.control_blocks[i].priority].remove(j)
			#print('removed, ', j)
		else:
			#print('in else statement of remove from RL or waitling list')
			for y in range(0,self.RCB.number_of_resource_blocks):
				if j in self.RCB.control_blocks[y].waitlist:
					#print('in waitlist if statement')
					self.RCB.control_blocks[y].waitlist.pop(j)


		#release all resources of j (call release(j) function)
		if len(self.PCB.control_blocks[i].resources)>0:
			q = list(self.PCB.control_blocks[i].resources)
			#print(q)
			for resource in q:
				#print('resource: '+str(resource))
				self.release(resource, 0, i)

		#free PCB of j X
		self.PCB.control_blocks.pop(i)
		#print(len(self.PCB.control_blocks), end='=len(self.PCB.control_blocks)')

		self.number_control_blocks = self.number_control_blocks - 1
		#this is for the current total of control blocks currently in this PCB after adding and destroying

		self.scheduler()
		self.head = self.RL[self.current_priority][0]

		#display: “n processes destroyed” X
		#print('process '+ str(j) +' destroyed')
		# (In order to release the resources of PCB[j] which is a
		# linked_list, must retrieve all the RCB number_ids and go to those respective RCB blocks
		# and check waitlist and if empty then make state ready=1 or remove the head of the list
		# and perhaps change the implicated processes of the PCB[k's] which were in the waiting
		# list?)

	#FUNCTION #3
	def request(self, resource: int, units: int):
		#print('Entered Request function')
		RL_head = self.RL[self.current_priority][0]
		index_RL_head = self.findindex(RL_head)
		# checked this error condition
		if (RL_head==0):
			#print('Current running process 0, cannot request resources.')
			return(-1)

		#checked this error condition
		if(resource > self.RCB.number_of_resource_blocks-1):
			#print('Requested resource does not exist!')
			return(-1)
		#checked this error condition
		if(units>self.RCB.control_blocks[resource].inventory):
			return (-1)
		#tested this error check, it worked once
		if resource in self.PCB.control_blocks[index_RL_head].resources:
			if ((units + self.PCB.control_blocks[index_RL_head].resources[resource]) > self.RCB.control_blocks[resource].inventory):
				#print('Error, request + resources presently held, exceeds total inventory of Process')
				return(-1)

		if(self.RCB.control_blocks[resource].state >= units):#if (r.state >= k) X
			self.RCB.control_blocks[resource].state = self.RCB.control_blocks[resource].state - units#r.state = r.state - k
			#Either process is holding some of this resource
			if(resource in self.PCB.control_blocks[index_RL_head].resources):
				currently_held = self.PCB.control_blocks[index_RL_head].resources[resource]
				new_held = units + currently_held
				self.PCB.control_blocks[index_RL_head].resources[resource] = new_held #insert (r, k) into i.resources
				#print('resource, units: ['+str(resource)+','+str(new_held)+'] allocated')
			else:#Or it does not hold any portion of this resource
				self.PCB.control_blocks[index_RL_head].resources[resource] = units #insert (r, k) into i.resources
				#print('resource '+str(resource)+' allocated '+str(units)+' units')

		else:
			self.PCB.control_blocks[index_RL_head].state = 0#i.state = blocked
			j = self.RL[self.current_priority].pop(0)#remove i from RL
			#this is a single integer value which present for all processes in RL in a list of three lists
			self.RCB.control_blocks[resource].waitlist[j] = units #insert (i, k) into r.waitlist
			#print('process ' +str(j)+', requesting '+str(units)+' units blocked')
			self.scheduler()#scheduler()
			self.head = self.RL[self.current_priority][0]

	#FUNCTION #4 resource is block in RCB, Units is if we are partially trying to free resouce
	#deletedblock is an index of a block which we are attempting to delete recursively
	def release(self, resource:int, units:int=0, deletedblock=None):

		#print(self.RL)
		if deletedblock==None:#there could be a problem with such a if clause
			#the purpose behind this clause was to distuingish it being called from userinterface
			#which should be head of RL or current running process
			RL_head = self.RL[self.current_priority][0]
			index_RL_head = self.findindex(RL_head)

			if(resource not in self.PCB.control_blocks[index_RL_head].resources):
				#print('Current running process does not hold this resource!')
				return(-1)

		else:#if not it could be called in a recursive release
			index_RL_head = deletedblock

		#remove (r, k) from i.resources
		k = self.PCB.control_blocks[index_RL_head].resources[resource]
		#retrieve value associated with the respective key
		#print(k, ' units associated with block: ', self.PCB.control_blocks[index_RL_head].number_id)
		#units is parameter which is input by users or else default=0
		if(units > k):
			#print('Error, release of input units exceed units held by process')
			return (-1)
		#if the value which user input>0 and the value which the process holds is greater than the input of units
		elif(units>0 and k > units):#first clause to distuingish being called by user, k = how many process is actually holding
			self.PCB.control_blocks[index_RL_head].resources[resource] = k - units
			#update the key value-pair
		else:
			#print('in else before popping a resource from a PCB block')
			self.PCB.control_blocks[index_RL_head].resources.pop(resource)
			# completely pop out key-value pair from resource dictionary
		#up till this point should be fine?
		#r.state = r.state + k
		if units>0:
			self.RCB.control_blocks[resource].state = self.RCB.control_blocks[resource].state + units
			#print(str(self.RCB.control_blocks[resource].state))
		else:
			self.RCB.control_blocks[resource].state = self.RCB.control_blocks[resource].state + k
			#print('Resource: '+str(resource)+'state = '+str(self.RCB.control_blocks[resource].state)+' in else where units=0')


		#while (r.waitlist != empty and r.state > 0)
		#print('before while loop in release function')
		while (self.RCB.control_blocks[resource].waitlist and self.RCB.control_blocks[resource].state > 0):
			#get next (j, k) from r.waitlist
			#print('in while loop')

			j = list(self.RCB.control_blocks[resource].waitlist.items())
			#should pop a key,value pair from waitlist dictionary could potentially
			#if (r.state >= k)
			#print(j)
			process = j[0][0]
			unit_request = j[0][1]
			#print('process on waitlist:' + str(j[0][0])+' units requested:'+ str(j[0][1]))
			#print('past, j = self.RCB.control_blocks[resource].waitlist.items()[0]')

			index_waitlist_process = self.findindex(process)
			if (self.RCB.control_blocks[resource].state >= unit_request):#j[1] refers to units requested by process
				#r.state = r.state - k
				self.RCB.control_blocks[resource].state = self.RCB.control_blocks[resource].state - unit_request
				#insert (r, k) into j.resources
				#have to distuingish between if process on waitlist also holds a portion of resourcee
				if resource not in self.PCB.control_blocks[index_waitlist_process].resources:
					self.PCB.control_blocks[index_waitlist_process].resources[resource] = unit_request
				else:
					currently_held = self.PCB.control_blocks[index_waitlist_process].resources[resource]
					new_held = unit_request + currently_held
					self.PCB.control_blocks[index_waitlist_process].resources[resource] = new_held
				#j.state = ready
				self.PCB.control_blocks[index_waitlist_process].state = 1
				#remove (j, k) from r.waitlist, which is an orderedDict()
				self.RCB.control_blocks[resource].waitlist.pop(process)
				#insert j into RL
				self.RL[self.PCB.control_blocks[index_waitlist_process].priority].append(process)
			else:
				break

		self.scheduler()
		self.head = self.RL[self.current_priority][0]

	#FUNCTION #5
	def timeout(self):
		#print('Entered timeout function')
		#print(self.RL)
		j = self.RL[self.current_priority].pop(0)
		self.RL[self.current_priority].append(j)
		#print(self.RL)
		self.scheduler()
		self.head = self.RL[self.current_priority][0]


	#FUNCTION #6
	def scheduler(self):
		if len(self.RL[2])== 0:
			if len(self.RL[1]) == 0:
				self.current_priority = 0
			else:
				self.current_priority = 1
		else:
			self.current_priority = 2
		#print('Process '+ str(self.RL[self.current_priority][0])+' is running')


class PCB:
	def __init__(self):
		self.number_control_blocks = 0
		self.control_blocks = [PControlBlock(self.number_control_blocks, 0)]

class PControlBlock:
	def __init__(self, number_id: int, priority: int, parent:int=None , children=[]):
		self.state = 1
		self.number_id = number_id
		self.parent = parent
		self.children = children
		self.resources = OrderedDict()
		self.priority = priority
		#print('Parent Process: '+ str(self.parent))

class RCB:
	def __init__(self, m):
		self.number_of_resource_blocks = m
		self.control_blocks = []
		for i in range(0,m):
			self.control_blocks.append(RControlBlock(i, i+1 if i==0 else i))#assoctiating the units to the blocks (0=1,1=1,2=2,3=3)

class RControlBlock:
	def __init__(self, number_id: int, units: int):
		self.number_id = number_id
		self.state = units
		self.inventory = units
		self.waitlist = OrderedDict()
		#dictionary would go inside the waitlist to associate an index with
		#the number of units requested by the process

def Shell_User_input():
	#Shell which will interact as hardware for the Process and Resource Manager
	infile = open("input.txt", "r")
	outfile = open("output.txt", "w")

	system = ProcessManager()


	for line in infile:

		if (line[:2] == 'in'):
			system.reset()
			print('\n',end='',file=outfile)
			print(str(system.head),end=' ',file=outfile)
			continue

		if (line[:2] == 'cr'):
			try:
				priority = int(line[3:])
				if (0 <= priority <= 2):
					a=system.create(priority)
					if a==-1:
						print(-1,end=' ',file=outfile)
					else:
						print(str(system.head),end=' ',file=outfile)
					continue
				else:
					print(-1,end=' ',file=outfile)
					continue
			except:
				print('In except block',end=' ',file=outfile)
				continue

		if (line[:2] == 'de'):
			try:
				#print(system.RL)
				process_j = int(line[3:])
				a=system.destroy(process_j)
				if a == -1:
					print(-1, end=' ',file=outfile)
				else:
					print(str(system.head),end=' ',file=outfile)
				continue
			except:
				print(-1, end=' ',file=outfile)
				continue

		if (line[:2] == 'rq'):
			try:
				resource_index = int(line[3])
				units = int(line[5])
				a=system.request(resource_index, units)
				if a == -1:
					print(-1, end=' ',file=outfile)
				else:
					print(str(system.head),end=' ',file=outfile)
				continue
			except:
				print('In except block',end=' ',file=outfile)
				continue

		if (line[:2] == 'rl'):
			try:
				resource_index = int(line[3])
				units= int(line[5])
				a=system.release(resource_index, units)
				if a == -1:
					print(-1, end=' ',file=outfile)
				else:
					print(str(system.head),end=' ',file=outfile)
				continue
			except:
				print('In except block',file=outfile)
				continue

		if (line[:2] == 'to'):
			try:
				system.timeout()
				print(str(system.head), end=' ',file=outfile)
				continue
			except:
				print('In except block',file=outfile)
				continue

		if (line[:2] == 'fi'):
			try:
				resource_index = int(line[3])
				system.findindex(resource_index)
			except:
				print('', end='',file=outfile)





	infile.close()
	outfile.close()
	
if __name__ == '__main__':
	Shell_User_input()

#Examples of conditions that must be detected and reported include
#Creating more than n processes X
#Destroying a process that is not a child of the current process X
#Requesting a nonexistent resource X
#Requesting a resource the process is already holding? what if the process is partially holding it?
#Releasing a resource the process is not holding X
#Process 0 should be prevented from requesting any resource to avoid the possibility of a deadlock where no process is
#on the RL. X
