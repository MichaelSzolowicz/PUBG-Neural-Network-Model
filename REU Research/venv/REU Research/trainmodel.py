import model
import torch
import matplotlib.pyplot as plt
import math
import csv
import imageio
import os


def train(m, x, y):
	opt = torch.optim.Adam(m.parameters(), lr=0.01)		# lr = learning rate
	loss_fn = torch.nn.MSELoss()
	ls = []
	y = y.nan_to_num()

	BATCHES = 3
	start = 0
	split = 0

	for i in range(100):
		for batch in range(BATCHES):
			x_size = x.size()[0]
			split += math.floor(x_size/BATCHES)

			# print(start)
			# print(split)

			_x = x[start:split]
			_y = y[start:split]

			start = split

			y_pred = m(_x)
			loss = loss_fn(y_pred, _y)
			opt.zero_grad()
			loss.backward()
			opt.step()
			print(loss)
			ls.append(loss)

		start = 0
		split = 0


def evaluation(m, x, y):
	y = y.nan_to_num()
	# y = y / y.max()
	loss_fn = torch.nn.MSELoss()
	return loss_fn(m(x), y)


def plot(m, val_x, val_y):
	pred_val_y = m(val_x)
	pred_rows = pred_val_y.tolist()
	val_y = val_y.nan_to_num()
	# val_y = val_y / val_y.max()
	actual_rows = val_y.tolist()

	plt.style.use('seaborn')
	plt.xlabel('X Coordinate')
	plt.ylabel('Y Coordinate')
	plt.title('Predicted Coordinates vs Actual Coordinates')

	largest_error = 0.0
	error_list = []
	all_errors_list = []
	filenames = []

	csv_reader = csv.reader(open('tensor_timestamps.csv'))
	timestamps = list(csv_reader)
	for i in range(0, len(pred_rows)):
		taken_coord = []
		for j in range(0, len(pred_rows[0]), 3):
			x_coord = [pred_rows[i][j]]
			y_coord = [pred_rows[i][j + 1]]
			smallest_error = 100
			nearest_x = 100
			nearest_y = 100
			for k in range(0, len(actual_rows[0]), 3):
				x = actual_rows[i][k]
				y = actual_rows[i][k + 1]
				if x == 0.0 and y == 0.0:
					break
				error = math.sqrt(((x - x_coord[0]) ** 2) + ((y - y_coord[0]) ** 2))
				current_coord = (x, y)
				if error < smallest_error and current_coord not in taken_coord:
					smallest_error = error
					nearest_x = x
					nearest_y = y
				if error > largest_error:
					largest_error = error
			taken_coord.append(current_coord)
			if smallest_error == 100:
				smallest_error = math.sqrt(((x - x_coord[0]) ** 2) + ((y - y_coord[0]) ** 2))
			else:
				error_list.append(smallest_error)
			all_errors_list.append(smallest_error)
			x_coord.append(nearest_x)
			y_coord.append(nearest_y)
			if x_coord[0] > 0.0001 and y_coord[0] > 0.0001:
				plt.plot(x_coord, y_coord, color='blue', marker='.')
				plt.plot(x_coord[1], y_coord[1], color='red', marker='.')
		error_list.clear()
		taken_coord.clear()

		plt.title('Predicted Coordinate vs. Actual Coordinate\nTimestamp: {0}'.format(timestamps[i][0]))
		plt.xlim(0, 1)
		plt.ylim(0, 1)
		plt.tight_layout()
		# plt.show()
		filename = 'PredictionsPlots/{0}.png'.format(i)
		filenames.append(filename)
		plt.savefig(filename)
		plt.clf()
		plt.cla()
		plt.close()

	average = sum(all_errors_list) / len(all_errors_list)
	print('Largest error: {0}\nSmallest error: {1}\nAverage error: {2}\n'.format(max(all_errors_list), min(all_errors_list), average))

	with imageio.get_writer('predictions.gif', mode='I') as writer:
		for filename in filenames:
			image = imageio.imread(filename)
			writer.append_data(image)

	for filename in set(filenames):
		os.remove(filename)


def main():
	m = model.load()

	train_x = torch.load('train_x.pt')
	train_y = torch.load('train_y.pt')
	train(m, train_x, train_y)

	val_x = torch.load('val_x.pt')
	val_y = torch.load('val_y.pt')
	loss = evaluation(m, val_x, val_y)

	print('Evaluation: {0}'.format(loss))

	# plot(m, val_x, val_y)

	val = input('Save Model? (Y/N): ')
	val = val.upper()
	if val == 'Y':
		model.save(m)
		print('Model saved!')
	else:
		print('Model not saved.')


if __name__ == "__main__":
	main()
