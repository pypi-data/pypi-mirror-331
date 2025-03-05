import math
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, BasicAer, execute

__version__ = '1.7'

def select(total_number):
  q=QuantumRegister(total_number)
  c=ClassicalRegister(total_number)
  qc=QuantumCircuit(q,c)
  qc.h(q[0])
  qc.cx(q[0],q[1])
  qc.x(q[1])
  if total_number>2:
    for index_limit in range(1,int(math.log(total_number,2))):
      index=-1
      while index< (2** index_limit)-1:
        index=index+1
        index1=index
        index2=index+ 2**index_limit
        qc.ch(q[index1],q[index2])
        qc.cx(q[index2],q[index1])
  qc.measure(q,c)
  backend_sim=BasicAer.get_backend('qasm_simulator')
  result=execute(qc,backend_sim).result()
  res=result.get_counts(qc)
  return res

def vis_circuit(total_number,file_name="circuit.png"):
  q=QuantumRegister(total_number)
  c=ClassicalRegister(total_number)
  qc=QuantumCircuit(q,c)
  qc.h(q[0])
  qc.cx(q[0],q[1])
  qc.x(q[1])
  if total_number>2:
    for index_limit in range(1,int(math.log(total_number,2))):
      index=-1
      while index< (2** index_limit)-1:
        index=index+1
        index1=index
        index2=index+ 2**index_limit
        qc.ch(q[index1],q[index2])
        qc.cx(q[index2],q[index1])
  qc.measure(q,c)
  fig = qc.draw(output='mpl', style="clifford")
  fig.savefig(file_name)